"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from doppel2.core.models import ScalarData, Unit, Metric, SensorGroup, Sensor
from datetime import datetime
from django.db.models import Avg
import json
from django.utils.timezone import make_aware, utc

BASE_API_URL = '/api/'
SCALAR_DATA_URL = BASE_API_URL + 'scalar_data/'
AGGREGATE_DATA_URL = BASE_API_URL + 'aggregate_scalar_data/'


class SensorDataTest(TestCase):
    def setUp(self):
        self.unit = Unit(name='C')
        self.unit.save()
        self.metric = Metric(name='Temperature')
        self.metric.save()
        self.sensor_group = SensorGroup(name="Thermostat")
        self.sensor_group.save()
        self.sensor = Sensor(unit=self.unit, sensor_group=self.sensor_group,
                             metric=self.metric)
        self.sensor.save()

    def test_data_can_be_added(self):
        data = ScalarData(sensor=self.sensor, value=25)
        data.save()
        self.assertEqual(data.sensor.unit.name, 'C')
        self.assertEqual(data.sensor.metric.name, 'Temperature')
        self.assertEqual(data.value, 25)

    def test_largeish_datasets_can_be_queried_quickly(self):
        data = [ScalarData(sensor=self.sensor, value=val)
                for val in range(10000)]
        ScalarData.objects.bulk_create(data)
        avg = 0
        start_time = datetime.now()
        #for data in ScalarData.objects.all():
        #    avg += data.value
        #avg = avg / ScalarData.objects.all().count()
        avg = ScalarData.objects.all().aggregate(Avg('value'))['value__avg']
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        # delete the data we created at the beginning of the test
        ScalarData.objects.all().delete()
        self.assertEqual(avg, 4999.5)
        self.assertLess(elapsed_time.total_seconds(), 0.1)


class ApiTest(TestCase):
    def setUp(self):
        self.unit = Unit(name='C')
        self.unit.save()
        self.metric = Metric(name='Temperature')
        self.metric.save()
        self.sensor_group = SensorGroup(name="Thermostat")
        self.sensor_group.save()
        self.sensor = Sensor(unit=self.unit, sensor_group=self.sensor_group,
                             metric=self.metric)
        self.sensor.save()

    def test_base_uri_should_be_gettable(self):
        base_response = self.client.get(BASE_API_URL,
                                        Accept="application/json")
        self.assertEqual(base_response.status_code, 200)

    def test_base_url_should_have_uri_for_scalar_data(self):
        base_response = self.client.get(BASE_API_URL,
                                        Accept="application/json")
        data = json.loads(base_response.content)
        self.assertEqual(data['scalar_data'], SCALAR_DATA_URL)

    def test_scalar_data_should_be_gettable_from_api(self):
        data = ScalarData(sensor=self.sensor, value=25)
        data.save()
        response = self.client.get(SCALAR_DATA_URL,
                                   Accept="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['objects']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], 25)
        self.assertEqual(data[0]['unit'], self.unit.name)
        self.assertEqual(data[0]['metric'], self.metric.name)

    def test_scalar_data_should_return_total_in_meta(self):
        data = ScalarData(sensor=self.sensor, value=25)
        data.save()
        # clear the id so we re-insert instead of updating
        data.id = None
        data.save()
        response = self.client.get(SCALAR_DATA_URL,
                                   Accept="application/json")
        self.assertEqual(response.status_code, 200)
        metadata = json.loads(response.content)['meta']
        self.assertEqual(metadata['total_count'], 2)

    def test_scalar_data_should_accept_a_date_range(self):
        data = []
        for value, hour in zip([20, 21, 23, 27], [2, 4, 6, 8]):
            data.append(
                ScalarData(sensor=self.sensor, value=value,
                           timestamp=make_aware(
                               datetime(2013, 4, 12, hour, 0, 0), utc)))
        ScalarData.objects.bulk_create(data)

        # create a date range that should only grab the middle 2 data points
        query_string = ('?timestamp__gt=2013-04-12T03:30:00Z&' +
                        'timestamp__lt=2013-04-12T06:30:00Z')
        url = SCALAR_DATA_URL + query_string
        response = self.client.get(url, Accept="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['objects']
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['value'], 21)
        self.assertEqual(data[1]['value'], 23)

    def test_aggregatescalar_data_should_give_average(self):
        data = []
        for value, hour in zip([20, 21, 23, 27], [2, 4, 6, 8]):
            data.append(
                ScalarData(sensor=self.sensor, value=value,
                           timestamp=make_aware(
                               datetime(2013, 4, 12, hour, 0, 0), utc)))
        ScalarData.objects.bulk_create(data)

        # create a date range that should only grab the middle 2 data points
        query_string = ('?timestamp__gt=2013-04-12T03:30:00Z&' +
                        'timestamp__lt=2013-04-12T06:30:00Z')
        url = AGGREGATE_DATA_URL + query_string
        response = self.client.get(url, Accept="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['objects']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['aggregate_value'], 22)
        self.assertEqual(data[0]['unit'], self.unit.name)
        self.assertEqual(data[0]['metric'], self.metric.name)



#class SensorDataApiTest(TestCase):
#    api_url = "api/"
#    def test_sensor_data_can_be_queried(self):
#        pass
