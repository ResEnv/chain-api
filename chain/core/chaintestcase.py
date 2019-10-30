from django.test import TestCase
from chain.core.models import Unit, Metric, Device, ScalarSensor, Site, \
    PresenceSensor, Person, Metadata
from chain.core.models import GeoLocation
from chain.core.api import HTTP_STATUS_SUCCESS, HTTP_STATUS_CREATED
from chain.core.hal import HALDoc
from chain.core import resources
from django.utils.timezone import now
from datetime import timedelta
import json

BASE_API_URL = '/'
ACCEPT_TAIL = 'application/xhtml+xml,application/xml;q=0.9,\
        image/webp,*/*;q=0.8'

class ChainTestCase(TestCase):
    # added this option so that we can disable adding the data by default
    # while we're testing the influx data migration
    write_scalar_data = True

    def setUp(self):
        self.unit = Unit(name='C')
        self.unit.save()
        self.temp_metric = Metric(name='temperature')
        self.temp_metric.save()
        self.setpoint_metric = Metric(name='setpoint')
        self.setpoint_metric.save()
        self.geo_locations = [
            GeoLocation(elevation=50, latitude=42.847, longitude=72.917),
            GeoLocation(elevation=-23.8, latitude=40.847, longitude=42.917)
        ]
        for loc in self.geo_locations:
            loc.save()
        self.metadata = []
        self.sites = [
            Site(name='Test Site 1',
                 geo_location=self.geo_locations[0],
                 raw_zmq_stream='tcp://example.com:8372'),
            Site(name='Test Site 2',
                 geo_location=self.geo_locations[1],
                 raw_zmq_stream='tcp://example.com:8172')
        ]
        for site in self.sites:
            site.save()
            self.metadata.append(Metadata(key="Test",
                                          value="Test Metadata 1",
                                          timestamp=now().isoformat(),
                                          content_object=site))
            self.metadata.append(Metadata(key="Test",
                                          value="Test Metadata 2",
                                          timestamp=now().isoformat(),
                                          content_object=site))

        num_devices = 2 * len(self.sites)
        self.devices = [Device(name='Thermostat %d' % i,
                               site=self.sites[i % len(self.sites)])
                        for i in range(0, num_devices)]
        num_people = 2 * len(self.sites)
        # self.people = [Person(first_name='John',
        #                       last_name = 'Doe %d' % i,
        #                       site=self.sites[i % len(self.sites)])
        #                for i in range(0, num_people)]
        # for person in self.people:
        #     person.save()
        self.sensors = []
        for device in self.devices:
            device.save()
            self.metadata.append(Metadata(key="Test",
                                          value="Test Metadata 1",
                                          timestamp=now().isoformat(),
                                          content_object=device))
            self.metadata.append(Metadata(key="Test",
                                          value="Test Metadata 2",
                                          timestamp=now().isoformat(),
                                          content_object=device))

            self.sensors.append(ScalarSensor(device=device,
                                             metric=self.temp_metric,
                                             unit=self.unit))
            self.sensors.append(ScalarSensor(device=device,
                                             metric=self.setpoint_metric,
                                             unit=self.unit))
        self.scalar_data = []
        for sensor in self.sensors:
            sensor.save()
            self.metadata.append(Metadata(key="Test",
                                          value="Test Metadata 1",
                                          timestamp=now().isoformat(),
                                          content_object=sensor))
            self.metadata.append(Metadata(key="Test",
                                          value="Test Metadata 1",
                                          timestamp=now().isoformat(),
                                          content_object=sensor))

            self.scalar_data.append({
                'sensor': sensor,
                'timestamp': now() - timedelta(minutes=2),
                'value': 22.0})
            self.scalar_data.append({
                'sensor': sensor,
                'timestamp': now() - timedelta(minutes=1),
                'value': 23.0})
        if self.write_scalar_data:
            for data in self.scalar_data:
                resources.influx_client.post_data(data['sensor'].device.site.id,
                                                  data['sensor'].device.id,
                                                  data['sensor'].id,
                                                  data['sensor'].metric,
                                                  data['value'],
                                                  data['timestamp'])
        for metadata in self.metadata:
            metadata.save()


    def get_resource(self, url, mime_type='application/hal+json',
                     expect_status_code=HTTP_STATUS_SUCCESS,
                     check_mime_type=True,
                     check_vary_header=True,
                     should_cache=None):
        accept_header = mime_type + ',' + ACCEPT_TAIL
        response = self.client.get(url,
                                   HTTP_ACCEPT=accept_header,
                                   HTTP_HOST='localhost')
        self.assertEqual(response.status_code, expect_status_code)
        if check_mime_type:
            self.assertEqual(response['Content-Type'], mime_type)
        if check_vary_header:
            # all resource responses should have the "Vary" header, which tells
            # intermediate caching servers that it needs to include the Accept
            # header in its cache lookup key
            self.assertIn(response['Vary'], "Accept")
        if should_cache is not None:
            if should_cache:
                self.assertIn("max-age", response['Cache-Control'])
            else:
                self.assertFalse(response.has_header('Cache-Control'))
        if response['Content-Type'] == 'application/hal+json':
            return HALDoc(json.loads(response.content))
        elif response['Content-Type'] == 'application/json':
            return json.loads(response.content)
        else:
            return response.content

    def create_resource(self, url, resource):
        return self.post_resource(url, resource, HTTP_STATUS_CREATED)

    def update_resource(self, url, resource):
        return self.post_resource(url, resource, HTTP_STATUS_SUCCESS)

    def post_resource(self, url, resource, expected_status):
        mime_type = 'application/hal+json'
        accept_header = mime_type + ',' + ACCEPT_TAIL
        response = self.client.post(url, json.dumps(resource),
                                    content_type=mime_type,
                                    HTTP_ACCEPT=accept_header,
                                    HTTP_HOST='localhost')
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response['Content-Type'], mime_type)
        if mime_type == 'application/hal+json':
            response_data = json.loads(response.content)
            if isinstance(response_data, list):
                return [HALDoc(d) for d in response_data]
            else:
                return HALDoc(response_data)
        elif mime_type == 'application/json':
            return json.loads(response.content)
        else:
            return response.content

    def get_sites(self, **kwargs):
        root = self.get_resource(BASE_API_URL)
        sites_url = root.links['ch:sites'].href
        return self.get_resource(sites_url, **kwargs)

    def get_a_site(self, **kwargs):
        '''GETs a site through the API for testing'''
        sites = self.get_sites()
        self.assertIn('items', sites.links)
        self.assertIn('href', sites.links.items[0])
        site_url = sites.links.items[0].href
        # following the link like a good RESTful client
        return self.get_resource(site_url, **kwargs)

    def get_devices(self, **kwargs):
        site = self.get_a_site()
        return self.get_resource(site.links['ch:devices'].href, **kwargs)

    # def get_a_person(self):
    #     site = self.get_a_site()
    #     people = self.get_resource(site.links['ch:people'].href)
    #     return self.get_resource(people.links['items'][0].href)
    #
    def get_a_device(self, **kwargs):
        '''GETs a device through the API for testing'''
        devices = self.get_devices()
        return self.get_resource(devices.links.items[0].href, **kwargs)

    def get_sensors(self, **kwargs):
        device = self.get_a_device()
        return self.get_resource(device.links['ch:sensors'].href, **kwargs)

    def get_a_sensor(self, **kwargs):
        sensors = self.get_sensors()
        return self.get_resource(sensors.links.items[0].href, **kwargs)

    def create_a_sensor_of_type(self, sensor_type):
        device = self.get_a_device()
        sensors = self.get_resource(device.links['ch:sensors'].href)
        sensor_url = sensors.links['createForm'].href

        new_sensor = {
            'sensor-type': sensor_type,
            'metric': 'rfid',
            'unit': 'N/A',
        }
        return self.create_resource(sensor_url, new_sensor)

    def get_a_sensor_of_type(self, sensor_type):
        sensors = self.get_sensors()
        for link in sensors.links.items:
            sensor = self.get_resource(link.href)
            if sensor['sensor-type'] == sensor_type:
                return sensor
        return self.create_a_sensor_of_type(sensor_type)

    def get_metadata(self):
        site = self.get_a_site()
        return self.get_resource(site.links['ch:metadata'].href)

    def get_site_device_sensor(self):
        return [self.get_a_site(), self.get_a_device(), self.get_a_sensor()]
