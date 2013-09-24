"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from doppel2.core.models import ScalarData, Unit, Metric, Device, Sensor, Site
from datetime import datetime
from django.db.models import Avg
import json
#from django.utils.timezone import make_aware, utc

BASE_API_URL = '/api/'
SCALAR_DATA_URL = BASE_API_URL + 'scalar_data/'
SITES_URL = BASE_API_URL + 'sites/'


class DoppelTestCase(TestCase):
    def setUp(self):
        self.unit = Unit(name='C')
        self.unit.save()
        self.temp_metric = Metric(name='Temperature')
        self.temp_metric.save()
        self.setpoint_metric = Metric(name='Setpoint')
        self.setpoint_metric.save()
        self.sites = [Site(name='Test Site 1'), Site(name='Test Site 2')]
        for site in self.sites:
            site.save()
        self.devices = [Device(name='Thermostat 1', site=self.sites[0]),
                        Device(name='Thermostat 2', site=self.sites[0]),
                        Device(name='Thermostat 3', site=self.sites[0]),
                        Device(name='Thermostat 4', site=self.sites[1]),
                        Device(name='Thermostat 5', site=self.sites[1])]
        for device in self.devices:
            device.save()
        self.sensors = []
        for device in self.devices:
            self.sensors.append(Sensor(device=device,
                                       metric=self.temp_metric,
                                       unit=self.unit))
            self.sensors.append(Sensor(device=device,
                                       metric=self.setpoint_metric,
                                       unit=self.unit))
        for sensor in self.sensors:
            sensor.save()

    def get_resource(self, url):
        response = self.client.get(url,
                                   Accept="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        return data


class SensorDataTest(DoppelTestCase):
    def test_data_can_be_added(self):
        data = ScalarData(sensor=self.sensors[0], value=25)
        data.save()
        self.assertEqual(data.value, 25)

    def test_largeish_datasets_can_be_queried_quickly(self):
        data = [ScalarData(sensor=self.sensors[0], value=val)
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


class ApiTest(DoppelTestCase):
    def test_base_url_should_have_href(self):
        data = self.get_resource(BASE_API_URL)
        self.assertEqual(data['href'], BASE_API_URL)

    def test_base_url_should_have_sites_collection(self):
        data = self.get_resource(BASE_API_URL)
        sites_coll = data['sites']
        self.assertEqual(sites_coll['href'], SITES_URL)

    def test_base_sites_collection_should_have_metadata(self):
        data = self.get_resource(BASE_API_URL)
        sites_coll = data['sites']
        self.assertEqual(sites_coll['meta']['total_count'], len(self.sites))

    def test_sites_should_be_expanded_in_base_url(self):
        response = self.get_resource(BASE_API_URL)
        sites = response['sites']['objects']
        self.assertIn(sites[0]['name'], [self.sites[0].name,
                                         self.sites[1].name])

    def test_site_resource_should_have_devices(self):
        base_response = self.get_resource(BASE_API_URL)
        sites = base_response['sites']['objects']
        site_url = sites[0]['href']
        # following the link like a good RESTful client
        site = self.get_resource(site_url)
        device_coll = self.get_resource(site['devices']['href'])
        db_site = Site.objects.get(name=site['name'])
        self.assertEqual(device_coll['meta']['total_count'],
                         db_site.devices.count())
        self.assertEqual(len(device_coll['objects']),
                         db_site.devices.count())

#    def test_scalar_data_should_be_gettable_from_api(self):
#        data = ScalarData(sensor=self.sensors[0], value=25)
#        data.save()
#        data = self.get_resource(SCALAR_DATA_URL)['objects']
#        self.assertEqual(len(data), 1)
#        self.assertEqual(data[0]['value'], 25)
#
#    def test_scalar_data_should_return_total_in_meta(self):
#        data = ScalarData(sensor=self.sensor, value=25)
#        data.save()
#        # clear the id so we re-insert instead of updating
#        data.id = None
#        data.save()
#        metadata = self.get_resource(SCALAR_DATA_URL)['meta']
#        self.assertEqual(metadata['total_count'], 2)


#class ScalarDataFilteringApiTest(DoppelTestCase):
#    def setUp(self):
#        DoppelTestCase.setUp(self)
#        device = Device(site=self.site, name="Thermostat")
#        device.save()
#        sensor1 = Sensor(unit=self.unit, device=device,
#                         metric=self.metric)
#        sensor1.save()
#        sensor2 = Sensor(unit=self.unit, device=device,
#                         metric=self.metric)
#        sensor2.save()
#        data = []
#        for value, hour in zip([20, 21, 23, 27], [2, 4, 6, 8]):
#            data.append(
#                ScalarData(sensor=sensor1, value=value,
#                           timestamp=make_aware(
#                               datetime(2013, 4, 12, hour, 0, 0), utc)))
#            data.append(
#                ScalarData(sensor=sensor2, value=value,
#                           timestamp=make_aware(
#                               datetime(2013, 4, 12, hour, 0, 0), utc)))
#        ScalarData.objects.bulk_create(data)
#
#    def test_scalar_data_should_accept_a_date_range(self):
#        # create a date range that should only grab the middle 2 data points
#        query_string = ('?timestamp__gt=2013-04-12T03:30:00Z&' +
#                        'timestamp__lt=2013-04-12T06:30:00Z')
#        url = SCALAR_DATA_URL + query_string
#        data = self.get_resource(url)['objects']
#        self.assertEqual(len(data), 4)
#
#    def test_scalar_data_should_accept_average(self):
#        query_string = ('?timestamp__gt=2013-04-12T03:30:00Z&' +
#                        'timestamp__lt=2013-04-12T06:30:00Z&' +
#                        'average_by=value')
#        url = SCALAR_DATA_URL + query_string
#        data = self.get_resource(url)
#        self.assertEqual(data['average_value'], 22)
