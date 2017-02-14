import requests
from pytz import UTC
from datetime import datetime
from django.db import IntegrityError
import itertools

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

    def post(self, sensor_id, value, timestamp=None):
        timestamp = InfluxClient.convert_timestamp(timestamp)
        data = '{0},sensor_id={1} value={2}'.format(self._measurement,
                                                    sensor_id,
                                                    value)
        if timestamp:
            data += ' ' + str(timestamp)
        response = self.request('POST',
                                self._url + '/write',
                                {'db': self._database},
                                data)
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
        query = "SELECT * FROM {0} WHERE sensor_id = \'{1}\' AND time >= {2} AND time < {3}".format(self._measurement,
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

    def get_databases(self):
        db={}
        response = self.get('SHOW DATABASES', False)
        values = response.json()['results'][0]['series'][0]['values']
        return [sub[0] for sub in values]

    def get_values(self,response):
        json = response.json()
        if len(json['results'])==0:
            return []
        if 'series' not in json['results'][0]:
            return []
        if len(json['results'][0]['series']) == 0:
            return []
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
