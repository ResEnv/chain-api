"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from doppel2.core.models import ScalarData, Unit, Metric
from datetime import datetime
from django.db.models import Avg
import json

BASE_API_URL = '/api/v1/'


class SensorDataTest(TestCase):
    def setUp(self):
        self.unit = Unit(name='C')
        self.unit.save()
        self.metric = Metric(name='Temperature')
        self.metric.save()

    def test_data_can_be_added(self):
        data = ScalarData(unit=self.unit, metric=self.metric, value=25)
        data.save()
        self.assertEqual(data.unit.name, 'C')
        self.assertEqual(data.metric.name, 'Temperature')
        self.assertEqual(data.value, 25)

    def test_largeish_datasets_can_be_queried_quickly(self):
        data = [ScalarData(unit=self.unit, metric=self.metric, value=val)
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
        unit = Unit(name='C')
        unit.save()
        metric = Metric(name='Temperature')
        metric.save()
        data = ScalarData(unit=unit, metric=metric, value=25)
        data.save()

    def test_base_uri_should_be_gettable(self):
        base_response = self.client.get(BASE_API_URL,
                                        Accept="application/json")
        self.assertEqual(base_response.status_code, 200)

    def test_scalar_data_should_be_gettable_from_api(self):
        base_response = self.client.get(BASE_API_URL + "scalar_data/",
                                        Accept="application/json")
        self.assertEqual(base_response.status_code, 200)
        data = json.loads(base_response.content)['objects']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], 25)
        self.assertEqual(data[0]['unit'], 'C')
        self.assertEqual(data[0]['metric'], 'Temperature')





#class SensorDataApiTest(TestCase):
#    api_url = "api/"
#    def test_sensor_data_can_be_queried(self):
#        pass
