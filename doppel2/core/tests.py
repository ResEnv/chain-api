"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from doppel2.core.models import ScalarData, Unit, Metric
from datetime import datetime
from django.db.models import Avg


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

    def test_large_datasets_can_be_queried(self):
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
        self.assertEqual(avg, 4999.5)
        self.assertLess(elapsed_time.total_seconds(), 0.1)
