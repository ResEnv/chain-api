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


class ScalarDataFilteringApiTest(TestCase):
    def setUp(self):
        unit = Unit(name='C')
        unit.save()
        metric = Metric(name='Temperature')
        metric.save()
        sensor_group = SensorGroup(name="Thermostat")
        sensor_group.save()
        sensor1 = Sensor(unit=unit, sensor_group=sensor_group,
                         metric=metric)
        sensor1.save()
        sensor2 = Sensor(unit=unit, sensor_group=sensor_group,
                         metric=metric)
        sensor2.save()
        data = []
        for value, hour in zip([20, 21, 23, 27], [2, 4, 6, 8]):
            data.append(
                ScalarData(sensor=sensor1, value=value,
                           timestamp=make_aware(
                               datetime(2013, 4, 12, hour, 0, 0), utc)))
            data.append(
                ScalarData(sensor=sensor2, value=value,
                           timestamp=make_aware(
                               datetime(2013, 4, 12, hour, 0, 0), utc)))
        ScalarData.objects.bulk_create(data)

    def test_scalar_data_should_accept_a_date_range(self):
        # create a date range that should only grab the middle 2 data points
        query_string = ('?timestamp__gt=2013-04-12T03:30:00Z&' +
                        'timestamp__lt=2013-04-12T06:30:00Z')
        url = SCALAR_DATA_URL + query_string
        response = self.client.get(url, Accept="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)['objects']
        self.assertEqual(len(data), 4)

    def test_scalar_data_should_accept_average(self):
        query_string = ('?timestamp__gt=2013-04-12T03:30:00Z&' +
                        'timestamp__lt=2013-04-12T06:30:00Z&' +
                        'average_by=value')
        url = SCALAR_DATA_URL + query_string
        response = self.client.get(url, Accept="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['average_value'], 22)

    def test_scalar_data_should_support_grouping(self):
        query_string = ('?group_by=sensor_uri')
        url = SCALAR_DATA_URL + query_string
        response = self.client.get(url, Accept="application/json")
        self.assertEqual(response.status_code, 200)
        groups = json.loads(response.content)['sensor_uri_groups']
        self.assertEqual(len(groups), 2)



#class SensorDataApiTest(TestCase):
#    api_url = "api/"
#    def test_sensor_data_can_be_queried(self):
#        pass
