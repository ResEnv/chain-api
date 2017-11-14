import requests
from pytz import UTC
from datetime import datetime
from django.db import IntegrityError
import itertools
from time import sleep
from chain.core.api import BadRequestException

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

    def post_data(self, site_id, device_id, sensor_id, value, timestamp=None):
        timestamp = InfluxClient.convert_timestamp(timestamp)
        data = '{0},sensor_id={1},site_id={2},device_id={3} value={4}'.format(self._measurement,
                                                                              sensor_id,
                                                                              site_id,
                                                                              device_id,
                                                                              value)
        if timestamp:
            data += ' ' + str(timestamp)
        response = self.post('write', data)
        if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
            raise IntegrityError('Error storing data')
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
        timestamp_gte = InfluxClient.convert_timestamp(filters['timestamp__gte'])
        timestamp_lt = InfluxClient.convert_timestamp(filters['timestamp__lt'])
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

        query = "SELECT * FROM {0} WHERE sensor_id = \'{1}\' AND time >= {2} AND time < {3}".format(measurement,
                                                                                                    filters['sensor_id'],
                                                                                                    timestamp_gte,
                                                                                                    timestamp_lt)
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
        # wait up to 15 seconds
        retries = 15
        series = {}
        # when influx first boots up the `values` field doesn't appear in the
        # result, so retry a few times
        while 'values' not in series and retries > 0:
            sleep(1)
            response = self.get('SHOW DATABASES', False)
            series = response.json()['results'][0]['series'][0]
            retries -= 1
        if 'values' not in series:
            raise Exception("Timed out waiting for InfluxDB to initialize")

        return [sub[0] for sub in series['values']]

    def get_values(self,response):
        json = response.json()
        if len(json['results'])==0:
            return []
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
            result = [dict(itertools.izip(columns, values[i])) for i in range(len(values))]
        return result


    @classmethod
    def convert_timestamp(cls, timestamp):
        if not timestamp.tzinfo:
            timestamp = UTC.localize(timestamp)
        return int((timestamp - EPOCH).total_seconds() * 1e9)
