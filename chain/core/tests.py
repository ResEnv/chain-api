from django.test import TestCase
from chain.core.models import ScalarData, Unit, Metric, Device, Sensor, Site
from chain.core.models import GeoLocation
#from chain.core.api import Resource
from datetime import datetime
import json
from chain.core.api import HTTP_STATUS_SUCCESS, HTTP_STATUS_CREATED
from django.utils.timezone import make_aware, utc
from chain.core.hal import HALDoc

HTTP_STATUS_NOT_ACCEPTABLE = 406
HTTP_STATUS_NOT_FOUND = 404

BASE_API_URL = '/api/'
SCALAR_DATA_URL = BASE_API_URL + 'scalar_data/'
SITES_URL = BASE_API_URL + 'sites/'


ACCEPT_TAIL = 'application/xhtml+xml,application/xml;q=0.9,\
        image/webp,*/*;q=0.8'


class HalTests(TestCase):
    def setUp(self):
        self.test_doc = {
            '_links': {'self': {'href': 'http://example.com'}},
            'attr1': 1,
            'attr2': 2
        }

    def test_basic_attrs_are_available(self):
        haldoc = HALDoc(self.test_doc)
        self.assertEqual(haldoc.attr1, self.test_doc['attr1'])
        self.assertEqual(haldoc.attr2, self.test_doc['attr2'])

    def test_links_is_an_attr_without_underscore(self):
        haldoc = HALDoc(self.test_doc)
        self.assertIn('self', haldoc.links)

    def test_link_href_is_available_as_attr(self):
        haldoc = HALDoc(self.test_doc)
        self.assertEqual(haldoc.links.self.href,
                         self.test_doc['_links']['self']['href'])

    def test_exception_raised_if_no_href_in_link(self):
        no_href = {'_links': {'nohref': {'title': 'A Title'}}}
        with self.assertRaises(ValueError):
            HALDoc(no_href)

    def test_links_should_allow_lists(self):
        doc = {
            '_links': {
                'self': {'href': 'http://example.com'},
                'children': [
                    {'href': 'http://example.com/children/1'},
                    {'href': 'http://example.com/children/2'}
                ]
            }
        }
        haldoc = HALDoc(doc)
        self.assertEquals(haldoc.links.children[0].href,
                          doc['_links']['children'][0]['href'])
        self.assertEquals(haldoc.links.children[1].href,
                          doc['_links']['children'][1]['href'])


class ChainTestCase(TestCase):
    def setUp(self):
        self.unit = Unit(name='C')
        self.unit.save()
        self.temp_metric = Metric(name='Temperature')
        self.temp_metric.save()
        self.setpoint_metric = Metric(name='Setpoint')
        self.setpoint_metric.save()
        self.geo_locations = [
            GeoLocation(elevation=50, latitude=42.847, longitude=72.917),
            GeoLocation(elevation=-23.8, latitude=40.847, longitude=42.917)
        ]
        for loc in self.geo_locations:
            loc.save()
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
        num_devices = 5
        self.devices = [Device(name='Thermostat %d' % i,
                               site=self.sites[i % len(self.sites)])
                        for i in range(0, num_devices)]
        self.sensors = []
        for device in self.devices:
            device.save()
            self.sensors.append(Sensor(device=device,
                                       metric=self.temp_metric,
                                       unit=self.unit))
            self.sensors.append(Sensor(device=device,
                                       metric=self.setpoint_metric,
                                       unit=self.unit))
        self.scalar_data = []
        for sensor in self.sensors:
            sensor.save()
            self.scalar_data.append(ScalarData(
                sensor=sensor,
                timestamp=make_aware(datetime(2013, 1, 1, 0, 0, 1), utc),
                value=22.0))
            self.scalar_data.append(ScalarData(
                sensor=sensor,
                timestamp=make_aware(datetime(2013, 1, 1, 0, 0, 2), utc),
                value=23.0))
        for data in self.scalar_data:
            data.save()

    def get_resource(self, url, mime_type='application/hal+json'):
        accept_header = mime_type + ',' + ACCEPT_TAIL
        response = self.client.get(url,
                                   HTTP_ACCEPT=accept_header)
        self.assertEqual(response.status_code, HTTP_STATUS_SUCCESS)
        self.assertEqual(response['Content-Type'], mime_type)
        if mime_type == 'application/hal+json':
            return HALDoc(json.loads(response.content))
        elif mime_type == 'application/json':
            return json.loads(response.content)
        else:
            return response.content

    def post_resource(self, url, resource, mime_type='application/hal+json'):
        accept_header = mime_type + ',' + ACCEPT_TAIL
        response = self.client.post(url, json.dumps(resource),
                                    content_type=mime_type,
                                    HTTP_ACCEPT=accept_header)
        self.assertEqual(response.status_code, HTTP_STATUS_CREATED)
        self.assertEqual(response['Content-Type'], mime_type)
        if mime_type == 'application/hal+json':
            return HALDoc(json.loads(response.content))
        elif mime_type == 'application/json':
            return json.loads(response.content)
        else:
            return response.content

    def get_sites(self):
        root = self.get_resource(BASE_API_URL)
        sites_url = root.links['ch:sites'].href
        return self.get_resource(sites_url)

    def get_a_site(self):
        '''GETs a site through the API for testing'''
        sites = self.get_sites()
        self.assertIn('items', sites.links)
        self.assertIn('href', sites.links.items[0])
        site_url = sites.links.items[0].href
        # following the link like a good RESTful client
        return self.get_resource(site_url)

    def get_devices(self):
        site = self.get_a_site()
        return self.get_resource(site.links['ch:devices'].href)

    def get_a_device(self):
        '''GETs a device through the API for testing'''
        devices = self.get_devices()
        return self.get_resource(devices.links.items[0].href)

    def get_sensors(self):
        device = self.get_a_device()
        return self.get_resource(device.links['ch:sensors'].href)

    def get_a_sensor(self):
        sensors = self.get_sensors()
        return self.get_resource(sensors.links.items[0].href)


class SensorDataTest(ChainTestCase):
    def test_data_can_be_added(self):
        data = ScalarData(sensor=self.sensors[0], value=25)
        data.save()
        self.assertEqual(data.value, 25)


class BasicHALJSONTests(ChainTestCase):
    def test_response_with_accept_hal_json_should_return_hal_json(self):
        response = self.client.get(BASE_API_URL,
                                   HTTP_ACCEPT='application/hal+json')
        self.assertEqual(response.status_code, HTTP_STATUS_SUCCESS)
        self.assertEqual(response['Content-Type'], 'application/hal+json')


class ApiRootTests(ChainTestCase):
    def test_root_should_have_self_rel(self):
        root = self.get_resource(BASE_API_URL,
                                 mime_type='application/hal+json')
        self.assertIn('self', root.links)
        self.assertIn('href', root.links.self)

    def test_root_should_have_curies_link(self):
        data = self.get_resource(BASE_API_URL)
        curies = data.links.curies
        self.assertEqual(curies[0].name, 'ch')
        self.assertRegexpMatches(curies[0].href, 'http://.*')

    def test_root_should_have_sites_link(self):
        data = self.get_resource(BASE_API_URL)
        sites_coll = data.links['ch:sites']
        self.assertRegexpMatches(sites_coll.href, 'http://.*' + SITES_URL)


class ApiSitesTests(ChainTestCase):
    def test_sites_coll_should_have_self_rel(self):
        sites = self.get_sites()
        self.assertIn('href', sites.links.self)

    def test_site_should_have_curies_link(self):
        site = self.get_a_site()
        curies = site.links.curies
        self.assertEqual(curies[0].name, 'ch')
        self.assertRegexpMatches(curies[0].href, 'http://.*')

    def test_sites_coll_should_have_curies_link(self):
        sites = self.get_sites()
        curies = sites.links.curies
        self.assertEqual(curies[0].name, 'ch')
        self.assertRegexpMatches(curies[0].href, 'http://.*')

    def test_sites_should_have_createform_link(self):
        sites = self.get_sites()
        self.assertIn('createForm', sites.links)
        self.assertIn('href', sites.links.createForm)
        self.assertEqual(sites.links.createForm.title, 'Create Site')

    def test_sites_should_have_items_link(self):
        sites = self.get_sites()
        self.assertIn('items', sites.links)

    def test_sites_links_should_have_title(self):
        sites = self.get_sites()
        self.assertIn(sites.links.items[0].title,
                      [s.name for s in self.sites])

    def test_sites_collection_should_have_total_count(self):
        sites = self.get_sites()
        self.assertEqual(sites.totalCount, len(self.sites))

    def test_site_should_have_self_link(self):
        site = self.get_a_site()
        self.assertIn('href', site.links.self)

    def test_site_should_have_name(self):
        site = self.get_a_site()
        self.assertIn(site.name, [s.name for s in self.sites])

    def test_site_should_have_devices_link(self):
        site = self.get_a_site()
        self.assertIn('ch:devices', site.links)
        self.assertIn('href', site.links['ch:devices'])
        devices = self.get_resource(site.links['ch:devices'].href)
        db_site = Site.objects.get(name=site.name)
        self.assertEqual(devices.totalCount, db_site.devices.count())

    def test_site_should_have_geolocation(self):
        site = self.get_a_site()
        self.assertIn('geoLocation', site)
        self.assertIn('elevation', site.geoLocation)
        self.assertIn(site.geoLocation['elevation'],
                      [l.elevation for l in self.geo_locations])
        self.assertIn('latitude', site.geoLocation)
        self.assertIn(site.geoLocation['latitude'],
                      [l.latitude for l in self.geo_locations])
        self.assertIn('longitude', site.geoLocation)
        self.assertIn(site.geoLocation['longitude'],
                      [l.longitude for l in self.geo_locations])

    def test_site_should_have_tidmarsh_zmq_link(self):
        site = self.get_a_site()
        self.assertIn('rawZMQStream', site.links)
        self.assertIn('href', site.links.rawZMQStream)

    def test_sites_should_be_postable(self):
        new_site = {
            'geoLocation': {
                'latitude': 42.360461,
                'longitude': -71.087347,
                'elevation': 12
            },
            'name': 'MIT Media Lab',
            '_links': {
                'rawZMQStream': {'href': 'tcp://example.com:8372'}
            }
        }
        sites = self.get_sites()
        response = self.post_resource(sites.links.createForm.href,
                                      new_site)
        db_obj = Site.objects.get(name='MIT Media Lab')
        self.assertEqual(new_site['name'], response.name)
        self.assertEqual(new_site['name'], db_obj.name)
        self.assertEqual(new_site['_links']['rawZMQStream']['href'],
                         response.links.rawZMQStream.href)
        self.assertEqual(new_site['_links']['rawZMQStream']['href'],
                         db_obj.raw_zmq_stream)
        for field in ['latitude', 'longitude', 'elevation']:
            self.assertEqual(new_site['geoLocation'][field],
                             response.geoLocation[field])
            self.assertEqual(new_site['geoLocation'][field],
                             getattr(db_obj.geo_location, field))


class ApiDeviceTests(ChainTestCase):
    def test_device_should_have_sensors_link(self):
        device = self.get_a_device()
        self.assertIn('ch:sensors', device.links)
        self.assertEqual('Sensors', device.links['ch:sensors'].title)

    def test_device_should_have_site_link(self):
        device = self.get_a_device()
        self.assertIn('ch:site', device.links)

    def test_device_should_have_curies_link(self):
        device = self.get_a_device()
        curies = device.links.curies
        self.assertEqual(curies[0].name, 'ch')
        self.assertRegexpMatches(curies[0].href, 'http://.*')

    def test_devices_coll_should_have_curies_link(self):
        devices = self.get_devices()
        curies = devices.links.curies
        self.assertEqual(curies[0].name, 'ch')
        self.assertRegexpMatches(curies[0].href, 'http://.*')

    def test_device_should_be_postable_to_a_site(self):
        site = self.get_a_site()
        devices = self.get_resource(site.links['ch:devices'].href)
        dev_url = devices.links.createForm.href
        new_device = {
            "building": "E14",
            "description": "A great device",
            "floor": "5",
            "name": "Unit Test Thermostat 42",
            "room": "E14-548R"
        }
        self.post_resource(dev_url, new_device)
        # make sure that a device now exists with the right name
        db_device = Device.objects.get(name=new_device['name'])
        # make sure that the device is set up in the right site
        db_site = Site.objects.get(name=site['name'])
        self.assertEqual(db_device.site, db_site)


class ApiSensorTests(ChainTestCase):
    def test_sensors_should_be_postable_to_existing_device(self):
        device = self.get_a_device()
        sensors = self.get_resource(device.links['ch:sensors'].href)
        sensor_url = sensors.links['createForm'].href

        new_sensor = {
            'metric': 'Bridge Length',
            'unit': 'Smoots',
        }
        self.post_resource(sensor_url, new_sensor)
        db_sensor = Sensor.objects.get(metric__name='Bridge Length',
                                       device__name=device.name)
        self.assertEqual('Smoots', db_sensor.unit.name)

    def test_sensors_should_be_postable_to_newly_posted_device(self):
        site = self.get_a_site()
        devices = self.get_resource(site.links['ch:devices'].href)

        new_device = {
            "building": "E14",
            "description": "A great device",
            "floor": "5",
            "name": "Unit Test Thermostat 49382",
            "room": "E14-548R"
        }
        device = self.post_resource(devices.links['createForm'].href,
                                    new_device)

        sensors = self.get_resource(device.links['ch:sensors'].href)
        new_sensor = {
            'metric': 'Beauty',
            'unit': 'millihelen',
        }
        self.post_resource(sensors.links['createForm'].href, new_sensor)
        db_sensor = Sensor.objects.get(metric__name='Beauty',
                                       device__name=device.name)
        self.assertEqual('millihelen', db_sensor.unit.name)

    def test_sensor_should_have_data_url(self):
        sensor = self.get_a_sensor()
        self.assertIn('ch:data_history', sensor.links)

    def test_sensor_should_have_parent_link(self):
        sensor = self.get_a_sensor()
        self.assertIn('ch:device', sensor.links)


#class ApiSensorDataTests(ChainTestCase):
#    def test_sensor_data_should_have_timestamp_and_value(self):
#        sensor = self.get_a_sensor()
#        sensor_data = self.get_resource(
#            sensor.links['ch:data_history'].href)
#        self.assertIn('timestamp', sensor_data.data[0])
#        self.assertIn('value', sensor_data.data[0])

#    def test_sensor_data_should_be_postable(self):
#        sensor = self.get_a_sensor()
#        data_url = sensor['history']['_href']
#        timestamp = make_aware(datetime(2013, 1, 1, 0, 0, 0), utc)
#        data = {
#            'value': 23,
#            'timestamp': timestamp.isoformat()
#        }
#        self.post_resource(data_url, data)
#        # TODO: actually make sure the posted data is correct


# these tests are testing specific URL conventions within this application
class CollectionFilteringTests(ChainTestCase):
    def test_devices_can_be_filtered_by_site(self):
        full_devices_coll = self.get_resource(BASE_API_URL + 'devices/')
        filtered_devices_coll = self.get_resource(
            BASE_API_URL + 'devices/?site=%d' % self.sites[0].id)
        self.assertEqual(len(full_devices_coll.links.items), 5)
        self.assertEqual(len(filtered_devices_coll.links.items), 3)

    def test_filtered_collection_has_filtered_url(self):
        site_id = self.sites[0].id
        coll = self.get_resource(
            BASE_API_URL + 'devices/?site=%d' % site_id)
        self.assertTrue(('site=%d' % site_id) in coll.links.self.href)
#
#    def test_device_collections_should_limit_to_default_page_size(self):
#        site = self.get_a_site()
#        devs_url = site['devices']['_href']
#        # make sure we create more devices than will fit on a page
#        for i in range(0, Resource.page_size + 1):
#            dev = {'name': 'test dev %d' % i}
#            self.post_resource(devs_url, dev)
#        devs = self.get_resource(devs_url)
#        self.assertEqual(len(devs['data']), Resource.page_size)
#
#    def test_pages_should_have_next_and_prev_links(self):
#        site = self.get_a_site()
#        devs_url = site['devices']['_href']
#        # make sure we create more devices than will fit on a page
#        for i in range(0, Resource.page_size + 1):
#            dev = {'name': 'test dev %d' % i}
#            self.post_resource(devs_url, dev)
#        devs = self.get_resource(devs_url)
#        self.assertIn('next', devs['meta'])
#        self.assertNotIn('previous', devs['meta'])
#        next_devs = self.get_resource(devs['meta']['next']['_href'])
#        self.assertIn('previous', next_devs['meta'])
#        self.assertNotIn('next', next_devs['meta'])


class HTMLTests(ChainTestCase):
    def test_root_request_accepting_html_gets_it(self):
        res = self.get_resource(BASE_API_URL, mime_type='text/html').strip()
        # check that it startswith a doctype
        self.assertTrue(res.startswith("<!DOCTYPE html"))
        self.assertTrue(res.endswith("</html>"))


class ErrorTests(TestCase):
    def test_unsupported_mime_types_should_return_406_status(self):
        response = self.client.get(BASE_API_URL, HTTP_ACCEPT='foobar')
        self.assertEqual(response.status_code, HTTP_STATUS_NOT_ACCEPTABLE)
        self.assertEqual(response['Content-Type'], 'application/hal+json')
        self.assertIn('message', json.loads(response.content))

    def test_if_client_accepts_wildcard_send_hal_json(self):
        response = self.client.get(BASE_API_URL, HTTP_ACCEPT='foobar, */*')
        self.assertEqual(response.status_code, HTTP_STATUS_SUCCESS)
        self.assertEqual(response['Content-Type'], 'application/hal+json')

    def test_bad_url_returns_404(self):
        response = self.client.get('/foobar/',
                                   HTTP_ACCEPT='application/hal+json')
        self.assertEqual(response.status_code, HTTP_STATUS_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/hal+json')
        self.assertIn('message', json.loads(response.content))
