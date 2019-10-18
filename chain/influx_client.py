import requests
from pytz import UTC
from datetime import datetime
from django.db import IntegrityError
import itertools
from time import sleep
from chain.core.api import BadRequestException
from itertools import izip

EPOCH = UTC.localize(datetime.utcfromtimestamp(0))

HTTP_STATUS_SUCCESSFUL_WRITE = 204

class InfluxClient(object):

    def __init__(self, host, port, database, measurement):
        self._host = host
        self._port = port
        self._database = database
        self._measurement = measurement
        # Persist TCP connection
        self._session = requests
        self._url = 'http://' + self._host + ':' + self._port

        if self._database not in self.get_databases():
            self.get('CREATE DATABASE ' + self._database)

    def request(self, method, url, params=None, data=None, headers=None):
        response = self._session.request(method=method,
                                         url=url,
                                         params=params,
                                         data=data,
                                         headers=headers)
        return response

    def post(self, endpoint, data, query=False):
        if endpoint == 'write':
            url = self._url + '/write'
        else:
            url = self._url + '/query'
        if query:
            data = {'q': data}
        response = self.request('POST',
                                url,
                                {'db': self._database},
                                data)
        return response

    def make_post_query_string(self, site_id, device_id, sensor_id, metric, value, timestamp=None):
        data = '{0},sensor_id={1},site_id={2},device_id={3},metric={4} value={5}'.format(self._measurement,
                                                                              sensor_id,
                                                                              site_id,
                                                                              device_id,
                                                                              metric,
                                                                              value)
        if timestamp:
            timestamp = InfluxClient.convert_timestamp(timestamp)
            data += ' ' + str(timestamp)
        return data

    def post_data(self, site_id, device_id, sensor_id, metric, value, timestamp=None):
        data = self.make_post_query_string(site_id, device_id, sensor_id, metric, value, timestamp)
        response = self.post('write', data)
        if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
            raise IntegrityError('Failed Query(status {}):\n{}\nResponse:\n{}'.format(response.status_code, data, response.json()))
        return response

    def post_data_bulk(self, site_id, device_id, sensor_id, metric, values, timestamps):
        query = ""
        for (value, timestamp) in izip(values, timestamps):
            query += self.make_post_query_string(site_id, device_id, sensor_id, metric, value, timestamp) + "\n"
        # print("posting query:\n{}\n".format(query))
        response = self.post('write', query)
        if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
            raise IntegrityError('Failed Query(status {}):\n{}\nResponse:\n{}'.format(response.status_code, data, response.json()))
        return response

    def get(self, query, database=False):
        # database arguement should be true for any sensor data queries
        if database:
            response = self.request('GET',
                                    self._url + '/query',
                                    {'db': self._database,'q': query})
        else:
            response = self.request('GET',
                                    self._url + '/query',
                                    {'q': query})

        return response

    def get_sensor_data(self, filters):
        if 'aggtime' not in filters:
            measurement = self._measurement
        # arguements are unicode strings
        elif filters['aggtime'] == u'1h':
            measurement = self._measurement + '_1h'
        elif filters['aggtime'] == u'1d':
            measurement = self._measurement + '_1d'
        elif filters['aggtime'] == u'1w':
            measurement = self._measurement + '_1w'
        else:
            raise BadRequestException('Invalid argument for aggtime. Must be 1h, 1d, or 1w')

        # exclude the old values that don't have metrics
        query = "SELECT * FROM {0} WHERE sensor_id = '{1}' AND metric != ''".format(measurement,
                                                                   filters['sensor_id'])
        if 'timestamp__gte' in filters:
            timestamp_gte = InfluxClient.convert_timestamp(filters['timestamp__gte'])
            query += ' AND time >= {}'.format(timestamp_gte)
        if 'timestamp__lt' in filters:
            timestamp_lt = InfluxClient.convert_timestamp(filters['timestamp__lt'])
            query += ' AND time < {}'.format(timestamp_lt)


        result = self.get_values(self.get(query, True))
        return result

    def get_last_sensor_data(self, sensor_id):
        query = "SELECT LAST(value) FROM {0} WHERE sensor_id = \'{1}\'".format(self._measurement,
                                                                           sensor_id)
        result = self.get_values(self.get(query, True))
        return result

    def get_last_data_from_all_sensors(self, site_id):
        query = "SELECT LAST(*) FROM {0} WHERE site_id = \'{1}\' GROUP BY sensor_id".format(self._measurement,
                                                                                           site_id)
        result = self.get_values(self.get(query, True))
        return result

    def get_databases(self):
        response = self.get('SHOW DATABASES', False)
        series = response.json()['results'][0]['series'][0]
        if 'values' not in series:
            # there's only a values list if there's at least one value
            return []

        return [sub[0] for sub in series['values']]

    # returns a list of dictionaries, with one dictionary for each series in the
    # query result. Each dictionary maps the column name to a list of data
    def get_values(self,response):
        json = response.json()
        try:
            if len(json['results'])==0:
                return []
        except:
            import pdb
            pdb.set_trace()
        if 'series' not in json['results'][0]:
            return []
        if len(json['results'][0]['series']) == 0:
            return []
        if 'tags' in json['results'][0]['series'][0]:
            series = json['results'][0]['series']
            result = []
            for d in series:
                values = d['values'][0]
                columns = d['columns']
                data = dict(itertools.izip(columns,values))
                data.update(d['tags'])
                result.append(data)
        else:
            series = json['results'][0]['series'][0]
            values = series['values']
            columns = series['columns']
            result = [dict(itertools.izip(columns, value)) for value in values]
        return result


    @classmethod
    def convert_timestamp(cls, timestamp):
        if not timestamp.tzinfo:
            timestamp = UTC.localize(timestamp)
        return int((timestamp - EPOCH).total_seconds() * 1e9)
