from chain.core.api import Resource, ResourceField, CollectionField
from chain.core.api import full_reverse
from chain.core.api import CHAIN_CURIES
from chain.core.api import BadRequestException
from chain.core.api import register_resource
from chain.core.models import Site, Device, ScalarSensor, \
    PresenceSensor, PresenceData, Person
from django.conf.urls import include, patterns, url
from django.utils import timezone
from datetime import timedelta, datetime
import calendar
from chain.localsettings import INFLUX_HOST, INFLUX_PORT, INFLUX_DATABASE, INFLUX_MEASUREMENT
from chain.influx_client import InfluxClient
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime


influx_client = InfluxClient(INFLUX_HOST, INFLUX_PORT, INFLUX_DATABASE, INFLUX_MEASUREMENT)

class SensorDataResource(Resource):

    def __init__(self, *args, **kwargs):
        super(SensorDataResource, self).__init__(*args, **kwargs)

    def format_time(self, timestamp):
        return calendar.timegm(timestamp.timetuple())

    def add_page_links(self, data, href, page_start, page_end):
        timespan = page_end - page_start
        data['_links']['previous'] = {
            'href': self.update_href(
                href, timestamp__gte=self.format_time(page_start - timespan),
                timestamp__lt=self.format_time(page_start)),
            'title': '%s to %s' % (page_start - timespan, page_start),
        }
        data['_links']['self'] = {
            'href': self.update_href(
                href, timestamp__gte=self.format_time(page_start),
                timestamp__lt=self.format_time(page_end)),
        }
        data['_links']['next'] = {
            'href': self.update_href(
                href, timestamp__gte=self.format_time(page_end),
                timestamp__lt=self.format_time(page_end + timespan)),
            'title': '%s to %s' % (page_end, page_end + timespan),
        }
        return data

class ScalarSensorDataResource(SensorDataResource):
    display_field = 'timestamp'
    resource_name = 'scalar_data'
    resource_type = 'scalar_data'
    model_fields = ['timestamp', 'value']
    schema_type = {'timestamp': ('string', 'date-time'),
                   'value': ('number', None)}
    required_fields = ['value']
    default_timespan = timedelta(hours=6)

    def __init__(self, *args, **kwargs):
        super(ScalarSensorDataResource, self).__init__(*args, **kwargs)
        if self._state == 'data':
            # deserialize data
            self.sensor_id = self._filters.get('sensor_id')
            self.value = self.sanitize_field_value('value', self._data.get('value'))
            self.timestamp = self.sanitize_field_value('timestamp', self._data.get('timestamp'))
            # add ids up the hierarchy
            sensor = ScalarSensor.objects.select_related('device').get(id=self.sensor_id)
            self.device_id = sensor.device.id
            self.site_id = sensor.device.site_id
            # treat sensor data like an object
            self._state = 'object'
        if 'queryset' in kwargs:
            # we want to default to the last page, not the first page
            pass

    def serialize_single(self, embed=True, cache=None, rels=True):
        data = {}
        for field_name in self.model_fields:
            data[field_name] = self.serialize_field(getattr(self, field_name))
        return data

    @classmethod
    def sanitize_field_value(cls, field_name, value):
        if field_name == 'value':
            return float(value)
        if field_name == 'timestamp':
            from django.db import models
            if value == None:
                return timezone.now()
            timestamp = parse_datetime(value)
            if timezone.is_aware(timestamp):
                return timestamp
            return timezone.make_aware(timestamp, timezone.get_current_timezone())


    def save(self):
        response = influx_client.post_data(self.site_id, self.device_id, self.sensor_id, self.value, self.timestamp)
        return response

    def serialize_list(self, embed, cache):
        '''a "list" of SensorData resources is actually represented
        as a single resource with a list of data points'''
        if not embed:
            return super(
                ScalarSensorDataResource,
                self).serialize_list(
                embed,
                cache)

        href = self.get_list_href()

        serialized_data = {
            '_links': {
                'curies': CHAIN_CURIES,
                'createForm': {
                    'href': self.get_create_href(),
                    'title': 'Add Data'
                }
            },
            'dataType': 'float'
        }
        request_time = timezone.now()

        # if the time filters aren't given then use the most recent timespan,
        # if they are given, then we need to convert them from unix time to use
        # in the queryset filter

        if 'timestamp__gte' in self._filters:
            try:
                page_start = datetime.utcfromtimestamp(
                    float(self._filters['timestamp__gte'])).replace(
                        tzinfo=timezone.utc)
            except ValueError:
                raise BadRequestException(
                    "Invalid timestamp format for lower bound of date range.")
        else:
            page_start = request_time - self.default_timespan

        if 'timestamp__lt' in self._filters:
            try:
                page_end = datetime.utcfromtimestamp(
                    float(self._filters['timestamp__lt'])).replace(
                        tzinfo=timezone.utc)
            except ValueError:
                raise BadRequestException(
                    "Invalid timestamp format for upper bound of date range.")
        else:
            page_end = request_time

        self._filters['timestamp__gte'] = page_start
        self._filters['timestamp__lt'] = page_end

        objs = influx_client.get_sensor_data(self._filters)
        serialized_data = self.add_page_links(serialized_data, href,
                                              page_start, page_end)
        serialized_data['data'] = [{
            'value': obj['value'],
            'timestamp': obj['time']}
            for obj in objs]
        return serialized_data

    def get_cache_key(self):
        return self.sensor_id, self.timestamp

    def serialize_stream(self):
        '''Serialize this resource for a stream'''
        data = self.serialize_single(rels=False)
        data['_links'] = {
            'ch:sensor': {'href': full_reverse(
                'scalar_sensors-single', self._request,
                args=(self._filters['sensor_id'],))}
        }
        return data

    def get_single_href(self):
        return full_reverse(self.resource_name + '-single',
                            self._request, args=(self.sensor_id,self.timestamp))

    def get_tags(self):
        if not self.sensor_id:
            raise ValueError(
                'Tried to called get_tags on a resource without an id')
        db_sensor = ScalarSensor.objects.select_related('device').get(
            id=self.sensor_id)
        return ['sensor-%d' % db_sensor.id,
                'device-%d' % db_sensor.device_id,
                'site-%d' % db_sensor.device.site_id]

    @classmethod
    def get_field_schema_type(cls, field_name):
        if field_name in cls.model_fields:
            return cls.schema_type[field_name]
        else:
            raise NotImplementedError(
                "tried to look up field %s but didn't know where" % field_name)
    
    @classmethod
    def model_has_field(cls, field_name):
        if field_name in cls.model_fields:
            return True
        return False


class AggregateScalarSensorDataResource(SensorDataResource):

    resource_name = 'aggregate_data'
    resource_type = 'aggregate_data'
    model_fields = ['timestamp', 'max', 'min', 'mean', 'count']
    default_timespan = timedelta(hours=6)

    def __init__(self, *args, **kwargs):
        super(AggregateScalarSensorDataResource, self).__init__(*args, **kwargs)

    def get_list_href(self, embed=False):
        href = super(AggregateScalarSensorDataResource, self).get_list_href()
        if not embed:
            href += '{&aggtime}'
        return href

    def serialize_list(self, embed, cache):
        if not embed:
            return super(
                AggregateScalarSensorDataResource,
                self).serialize_list(
                embed,
                cache)

        if 'aggtime' not in self._filters:
            raise BadRequestException(
                "Missing aggtime arguement")

        href = self.get_list_href(True)

        serialized_data = {
            '_links': {
                'curies': CHAIN_CURIES
            },
            'dataType': 'float'
        }
        request_time = timezone.now()

        if 'timestamp__gte' in self._filters:
            try:
                page_start = datetime.utcfromtimestamp(
                    float(self._filters['timestamp__gte'])).replace(
                        tzinfo=timezone.utc)
            except ValueError:
                raise BadRequestException(
                    "Invalid timestamp format for lower bound of date range.")
        else:
            page_start = request_time - self.default_timespan

        if 'timestamp__lt' in self._filters:
            try:
                page_end = datetime.utcfromtimestamp(
                    float(self._filters['timestamp__lt'])).replace(
                        tzinfo=timezone.utc)
            except ValueError:
                raise BadRequestException(
                    "Invalid timestamp format for upper bound of date range.")
        else:
            page_end = request_time

        self._filters['timestamp__gte'] = page_start
        self._filters['timestamp__lt'] = page_end
        objs = influx_client.get_sensor_data(self._filters)

        serialized_data = self.add_page_links(serialized_data, href,
                                              page_start, page_end)
        serialized_data['data'] = [{
            'max': obj['max'],
            'min': obj['min'],
            'mean': obj['mean'],
            'count': obj['count'],
            'timestamp': obj['time']}
            for obj in objs]
        
        return serialized_data


    @classmethod
    def urls(cls):
        base_name = cls.resource_name
        return patterns('',
                        url(r'^$',
                            cls.list_view, name=base_name + '-list'))



class ScalarSensorResource(Resource):

    model = ScalarSensor
    display_field = 'metric'
    resource_name = 'scalar_sensors'
    resource_type = 'scalar_sensor'
    required_fields = ['metric', 'unit']
    model_fields = ['active']

    # for now, name is hardcoded as the only attribute of metric and unit
    stub_fields = {'metric': 'name', 'unit': 'name'}
    queryset = ScalarSensor.objects
    related_fields = {
        'ch:dataHistory': CollectionField(ScalarSensorDataResource,
                                          reverse_name='sensor'),
        'ch:aggregateData': CollectionField(AggregateScalarSensorDataResource,
                                            reverse_name='sensor'),
        'ch:device': ResourceField('chain.core.resources.DeviceResource',
                                   'device')
    }

    def serialize_single(self, embed, cache, *args, **kwargs):
        data = super(
            ScalarSensorResource,
            self).serialize_single(
            embed,
            cache,
            *args,
            **kwargs)

        data['sensor-type'] = "scalar"
        if embed:
            data['dataType'] = 'float'
            # this is hammering the influx server, we should switch it
            # over to doing a single bulk query. For now disabling the
            # data to get things up and running
            if not kwargs.get('include_data', True):
                return data
            else:
                last_data = influx_client.get_last_sensor_data(self._obj.id)
                if last_data:
                    # column name returned by last() selector is last
                    data['value'] = last_data[0]['last']
                    data['updated'] = last_data[0]['time']
        return data

    def get_tags(self):
        return ['sensor-%s' % self._obj.id,
                'scalar_sensor-%s' % self._obj.id,
                'device-%s' % self._obj.device_id,
                'site-%s' % self._obj.device.site_id]


class PresenceDataResource(SensorDataResource):
    model = PresenceData
    display_field = 'timestamp'
    resource_name = 'presencedata'
    resource_type = 'presencedata'
    model_fields = ['timestamp', 'present', 'person', 'sensor']
    required_fields = ['person', 'sensor', 'present']
    queryset = PresenceData.objects
    default_timespan = timedelta(hours=6)

    def __init__(self, *args, **kwargs):
        super(PresenceDataResource, self).__init__(*args, **kwargs)
        if 'queryset' in kwargs:
            # we want to default to the last page, not the first page
            pass

    def serialize_single(self, embed, cache):
        serialized_data = super(
            PresenceDataResource,
            self).serialize_single(
            embed,
            cache)
        if 'person' in serialized_data:
            del serialized_data['person']
        if 'sensor' in serialized_data:
            del serialized_data['sensor']
        if '_links' not in serialized_data:
            serialized_data['_links'] = {}
        serialized_data['_links'].update(self.get_additional_links())
        return serialized_data

    def get_additional_links(self):
        return {
            'person': {
                'href': self.get_person_url(
                    self._obj.person), 'title': "%s, %s" %
                (self._obj.person.last_name, self._obj.person.first_name)}, 'sensor': {
                'href': self.get_sensor_url(
                    self._obj.sensor), 'title': "%s->%s" %
                (self._obj.sensor.device.name, self._obj.sensor.metric)}}

    def serialize_list(self, embed, cache):
        '''a "list" of SensorData resources is actually represented
        as a single resource with a list of data points'''
        if not embed:
            return super(
                PresenceDataResource,
                self).serialize_list(
                embed,
                cache)

        href = self.get_list_href()

        items = []

        serialized_data = {
            '_links': {
                'curies': CHAIN_CURIES,
                'createForm': {
                    'href': self.get_create_href(),
                    'title': 'Add Data'
                },
                'items': items
            },
            'dataType': 'presence'
        }
        request_time = timezone.now()

        # if the time filters aren't given then use the most recent timespan,
        # if they are given, then we need to convert them from unix time to use
        # in the queryset filter
        if 'timestamp__gte' in self._filters:
            try:
                page_start = datetime.utcfromtimestamp(
                    float(self._filters['timestamp__gte']))
            except ValueError:
                raise BadRequestException(
                    "Invalid timestamp format for lower bound of date range.")
        else:
            page_start = request_time - self.default_timespan

        if 'timestamp__lt' in self._filters:
            try:
                page_end = datetime.utcfromtimestamp(
                    float(self._filters['timestamp__lt']))
            except ValueError:
                raise BadRequestException(
                    "Invalid timestamp format for upper bound of date range.")
        else:
            page_end = request_time

        self._filters['timestamp__gte'] = page_start
        self._filters['timestamp__lt'] = page_end

        objs = self._queryset.filter(**self._filters).order_by('timestamp')

        serialized_data = self.add_page_links(serialized_data, href,
                                              page_start, page_end)

        # Make links:
        for obj in objs:
            presence_data_resource = PresenceDataResource(
                obj=obj,
                request=self._request)
            items.append(
                {
                    'href': presence_data_resource.get_single_href(),
                    'title': "%s %s %s at time %s" %
                    (obj.person.last_name,
                     "at" if obj.present else "left",
                     obj.sensor.device,
                     obj.timestamp.isoformat())})
        return serialized_data

    def get_person_url(self, obj):
        if self._request is None:
            # No way to form URL, just return the person's ID
            return obj.id
        person_resource = PersonResource(obj=obj, request=self._request)
        return person_resource.get_single_href()

    def get_sensor_url(self, obj):
        if self._request is None:
            # No way to form URL, just return the person's ID
            return obj.id
        psensor_resource = PresenceSensorResource(
            obj=obj,
            request=self._request)
        return psensor_resource.get_single_href()

    def serialize_stream(self):
        '''Serialize this resource for a stream'''
        data = self.serialize_single(False, None)  # (rels=False)
        # TODO:  Make useful
        data['_links'] = {
            'href': self.get_single_href(),
            #'person':
        }
        data['_links'].update(self.get_additional_links())
        return data

    def get_tags(self):
        if not self._obj:
            raise ValueError(
                'Tried to called get_tags on a resource without an object')
        db_sensor = PresenceSensor.objects.select_related('device').get(
            id=self._obj.sensor_id)
        return ['person-%d' % self._obj.person_id,
                'sensor-%d' % db_sensor.id,
                'device-%d' % db_sensor.device_id,
                'site-%d' % db_sensor.device.site_id]

    def get_filled_schema(self):
        schema = super(PresenceDataResource, self).get_filled_schema()
        # we need to replace the sensor and/or person links with just
        # the URL instead of the full object
        props = schema['properties']
        if 'person' in props:
            person_default = props['person']['default']
            props['person']['default'] = self.get_person_url(person_default)
        if 'sensor' in props:
            sensor_default = props['sensor']['default']
            props['sensor']['default'] = self.get_sensor_url(sensor_default)
        return schema


class PresenceSensorResource(Resource):
    model = PresenceSensor
    display_field = 'metric'
    resource_name = 'presence_sensors'
    resource_type = 'presence_sensor'
    required_fields = ['metric']

    # for now, name is hardcoded as the only attribute of metric and unit
    stub_fields = {'metric': 'name'}
    queryset = PresenceSensor.objects
    related_fields = {
        'ch:dataHistory': CollectionField(PresenceDataResource,
                                          reverse_name='sensor'),
        'ch:device': ResourceField('chain.core.resources.DeviceResource',
                                   'device')
    }

    def serialize_single(self, embed, cache, *args, **kwargs):
        data = super(
            PresenceSensorResource,
            self).serialize_single(
            embed,
            cache,
            *args,
            **kwargs)
        data['sensor-type'] = "presence"
        data['dataType'] = "presence"
        if embed:
            if '_embedded' not in data:
                data['_embedded'] = {}
            data['_embedded'].update(self.get_additional_embedded())
        if '_links' not in data:
            data['_links'] = {}
        data['_links'].update(self.get_additional_links())
        return data

    def get_additional_links(self):
        links = {}
        last_data = self._obj.presence_data.order_by(
            'timestamp').reverse()[:1]
        if last_data:
            links['last-visit'] = {
                'href': self.get_presense_data_url(
                    last_data[0]), 'title': "%s at %s" %
                (last_data[0].person, last_data[0].timestamp.isoformat())}
        return links

    def get_additional_embedded(self):
        embedded = {}
        last_data = self._obj.presence_data.order_by(
            'timestamp').reverse()[:1]
        if last_data:
            embedded['last-visit'] = PresenceDataResource(obj=last_data[0], request=self._request)\
                .serialize_single(False, {})
        return embedded

    def get_person_url(self, obj):
        if self._request is None:
            # No way to form URL, just return the person's ID
            return obj.id
        person_resource = PersonResource(obj=obj, request=self._request)
        return person_resource.get_single_href()

    def get_presense_data_url(self, obj):
        if self._request is None:
            # No way to form URL, just return the person's ID
            return obj.id
        pdata_resource = PresenceDataResource(obj=obj, request=self._request)
        return pdata_resource.get_single_href()

    def get_sensor_url(self, obj):
        if self._request is None:
            # No way to form URL, just return the person's ID
            return obj.id
        psensor_resource = PresenceSensorResource(
            obj=obj,
            request=self._request)
        return psensor_resource.get_single_href()

    def get_tags(self):
        return ['sensor-%s' % self._obj.id,
                'presense_sensor-%s' % self._obj.id,
                'device-%s' % self._obj.device_id,
                'site-%s' % self._obj.device.site_id]


class PersonResource(Resource):

    model = Person
    display_field = 'last_name'
    resource_name = 'people'
    resource_type = 'person'
    required_fields = ['first_name', 'last_name']
    model_fields = ['first_name', 'last_name', 'twitter_handle', 'rfid']
    related_fields = {
        'ch:presence-data': CollectionField(PresenceDataResource,
                                            reverse_name='person'),
        'ch:site': ResourceField('chain.core.resources.SiteResource', 'site')
    }
    queryset = Person.objects

    def serialize_single(self, embed, cache, *args, **kwargs):
        data = super(
            PersonResource,
            self).serialize_single(
            embed,
            cache,
            *args,
            **kwargs)
        if embed:
            if '_embedded' not in data:
                data['_embedded'] = {}
            data['_embedded'].update(self.get_additional_embedded())
        if '_links' in data:
            data['_links'].update(self.get_additional_links())
        return data

    def get_presence_data(self):
        filters = {
            'person': self._obj
        }
        return PresenceData.objects.filter(**filters).order_by('timestamp')[:1]

    def get_additional_links(self):
        links = {}
        last_data = self.get_presence_data()
        if last_data:
            links['last-visit'] = {
                'href': self.get_presense_data_url(
                    last_data[0]),
                'title': "at %s->%s at time %s" %
                (last_data[0].sensor.device,
                 last_data[0].sensor.metric,
                 last_data[0].timestamp.isoformat())}
        if self._obj.picture_url:
            links['picture'] = {
                'href': self._obj.picture_url,
                'title': 'Picture URL (external)'
            }
        return links

    def get_additional_embedded(self):
        embedded = {}
        last_data = self.get_presence_data()
        if last_data:
            embedded['last-visit'] = PresenceDataResource(obj=last_data[0], request=self._request)\
                .serialize_single(False, {})
        return embedded

    def get_presense_data_url(self, obj):
        if self._request is None:
            # No way to form URL, just return the person's ID
            return obj.id
        pdata_resource = PresenceDataResource(obj=obj, request=self._request)
        return pdata_resource.get_single_href()

    def get_tags(self):
        # sometimes the site_id field is unicode? weird
        return ['person-%d' % self._obj.id,
                'site-%s' % self._obj.site_id]


'''
Merge two "JSON" style dictionary/list objects
  recursively.  Designed for merging schemas from
  multiple sensor objects.

If two objects are not merge-able, the version from
  obj1 is used.
'''


def json_merge(obj1, obj2):
    if isinstance(obj1, list):
        # Merge array:
        set_used = set(obj1)
        new_arr = obj1[:]
        for el in obj2:
            if el not in set_used:
                new_arr.append(el)
        return new_arr
    elif isinstance(obj1, dict):
        # Merge object:
        new_obj = {}
        for key in obj1:
            if key in obj2:
                new_obj[key] = json_merge(obj1[key], obj2[key])
            else:
                new_obj[key] = obj1[key]
        for key in obj2:
            if key not in new_obj:
                new_obj[key] = obj2[key]
        return new_obj
    else:
        # Could not merge.  Select the version from
        #   the first object:
        return obj1


class MixedSensorResource(Resource):

    model = ScalarSensor
    display_field = 'metric'
    resource_name = 'sensors'
    resource_type = 'sensor'

    # for now, name is hardcoded as the only attribute of metric and unit
    stub_fields = {'metric': 'name'}

    queryset = ScalarSensor.objects

    available_sensor_types = {
        'scalar': {
            'model': ScalarSensor,
            'resource': ScalarSensorResource
        },
        'presence': {
            'model': PresenceSensor,
            'resource': PresenceSensorResource
        }
    }

    related_fields = {
        'ch:device': ResourceField('chain.core.resources.DeviceResource',
                                   'device')
    }

    @classmethod
    def get_schema(cls, filters=None):
        schema = {
            'required': ['sensor-type'],
            'type': 'object',
            'properties': {
                'sensor-type': {
                    'type': 'string',
                    'title': 'sensor-type',
                    'enum': cls.available_sensor_types.keys()
                }
            },
            'title': 'Create Sensor'
        }
        for sensor_type in cls.available_sensor_types:
            sub_schema = cls.available_sensor_types[
                sensor_type]['resource'].get_schema(filters)
            schema = json_merge(schema, sub_schema)
        return schema

    @classmethod
    def create_list(cls, data, req):
        raise Exception("Not yet implemented.")

    @classmethod
    def create_single(cls, data, req):
        if u'sensor-type' not in data:
            # raise Exception("'type' property not found")
            # For temporary back-compatability, assume it
            #   is a ScalarSensor:
            return ScalarSensorResource.create_single(data, req)
        for sensor_type in cls.available_sensor_types:
            if data['sensor-type'] == sensor_type:
                del data['sensor-type']
                return cls.available_sensor_types[sensor_type][
                    'resource'].create_single(data, req)
        # TODO:  Return 400 rather than raising an exception
        raise Exception("Unrecognized sensor type.")

    def serialize_single(self, embed, cache, *args, **kwargs):
        data = super(
            MixedSensorResource,
            self).serialize_single(
            embed,
            cache,
            *args,
            **kwargs)
        if embed:
            pass
        if '_links' in data:
            data['_links'].update(self.get_links())
            data['totalCount'] = len(data['_links']['items'])
        return data

    def serialize_list(self, embed, cache, *args, **kwargs):
        data = super(
            MixedSensorResource,
            self).serialize_list(
            embed=embed,
            cache=cache,
            *args,
            **kwargs)
        if embed:
            pass
        if '_links' in data:
            data['_links'].update(self.get_links())
            data['totalCount'] = len(data['_links']['items'])
        return data

    def get_links(self):
        mapped_model_to_res = self.map_model_to_resource()
        sensors = self.query_models()
        items = []
        for sensor in sensors:
            items.append(
                {
                    'href': (
                        mapped_model_to_res[
                            type(sensor)](
                            obj=sensor,
                            request=self._request)).get_single_href(),
                    'title': "%s" %
                    sensor})
        return {'items': items}

    def map_model_to_resource(self):
        mapped = {}
        for sensor_type in self.available_sensor_types:
            sensor_details = self.available_sensor_types[sensor_type]
            mapped[sensor_details['model']] = sensor_details['resource']
        return mapped

    def query_models(self):
        results = []
        for sensor_type in self.available_sensor_types:
            modelResults = self.available_sensor_types[sensor_type][
                'model'].objects.filter(**self._filters)
            results.extend(modelResults)
        return results

    def get_tags(self):
        return ['sensor-%s' % self._obj.id,
                'device-%s' % self._obj.device_id,
                'site-%s' % self._obj.device.site_id]


class DeviceResource(Resource):

    model = Device
    display_field = 'name'
    resource_name = 'devices'
    resource_type = 'device'
    required_fields = ['name']
    model_fields = ['name', 'description', 'building', 'floor', 'room', 'active']
    ''''ch:sensors': CollectionField(ScalarSensorResource,
                                      reverse_name='device'),
        'ch:sensors': CollectionField(PresenceSensorResource,
                                      reverse_name='device'),'''
    related_fields = {
        'ch:sensors': CollectionField(MixedSensorResource,
                                      reverse_name='device'),
        'ch:site': ResourceField('chain.core.resources.SiteResource', 'site')
    }
    queryset = Device.objects

    def get_tags(self):
        # sometimes the site_id field is unicode? weird
        return ['device-%d' % self._obj.id,
                'site-%s' % self._obj.site_id]


class SiteResource(Resource):

    model = Site

    # TODO _href should be the external URL if present

    resource_name = 'sites'
    resource_type = 'site'
    display_field = 'name'
    model_fields = ['name']
    required_fields = ['name']
    related_fields = {
        'ch:devices': CollectionField(DeviceResource, reverse_name='site'),
        'ch:people': CollectionField(PersonResource, reverse_name='site')
    }
    queryset = Site.objects

    def serialize_single(self, embed, cache):
        data = super(SiteResource, self).serialize_single(embed, cache)
        if embed:
            stream = self._obj.raw_zmq_stream
            if stream:
                data['_links']['rawZMQStream'] = {
                    'href': stream,
                    'title': 'Raw ZMQ Stream'}
            data['_links']['ch:siteSummary'] = {
                'title': 'Summary',
                'href': full_reverse('site-summary', self._request,
                                     args=(self._obj.id,))
            }
        return data

    def get_filled_schema(self):
        schema = super(SiteResource, self).get_filled_schema()
        schema['properties']['rawZMQStream']['default'] = \
            self._obj.raw_zmq_stream
        return schema

    def deserialize(self):
        super(SiteResource, self).deserialize()
        if 'rawZMQStream' in self._data:
            self._obj.raw_zmq_stream = self._data['rawZMQStream']
        return self._obj

    def update(self, data):
        super(SiteResource, self).update(data)
        if 'rawZMQStream' in data:
            self._obj.raw_zmq_stream = data['rawZMQStream']
        self._obj.save()

    def get_tags(self):
        return ['site-%d' % self._obj.id]

    @classmethod
    def get_schema(cls, filters=None):
        schema = super(SiteResource, cls).get_schema(filters)
        schema['properties']['rawZMQStream'] = {
            'type': 'string',
            'format': 'uri',
            'title': 'rawZMQStream'
        }
        return schema

    @classmethod
    def site_summary_view(cls, request, id):
        #filters = request.GET.dict()
        devices = Device.objects.filter(site_id=id).select_related(
            'sensors',
            'sensors__metric',
            'sensors__unit'
        )
        response = {
            '_links': {
                'self': {'href': full_reverse('site-summary', request,
                                              args=(id,))},
            },
            'devices': []
        }
        sensor_data_list = influx_client.get_last_data_from_all_sensors(id)
        sensor_data_dict = {}
        for data_point in sensor_data_list:
            sensor_data_dict[int(data_point['sensor_id'])] = (data_point['last_value'], data_point['time'])
        for device in devices:
            dev_resource = DeviceResource(obj=device, request=request)
            dev_data = dev_resource.serialize(rels=False)
            dev_data['href'] = dev_resource.get_single_href()
            response['devices'].append(dev_data)
            dev_data['sensors'] = []
            for sensor in device.sensors.all():
                sensor_resource = ScalarSensorResource(
                    obj=sensor,
                    request=request)
                sensor_data = sensor_resource.serialize(rels=False, include_data=False)
                try:
                    sensor_data['value'] = sensor_data_dict[sensor.id][0]
                    sensor_data['updated'] = sensor_data_dict[sensor.id][1]
                except KeyError:
                    # looks like we don't have any data for this sensor
                    pass
                sensor_data['href'] = sensor_resource.get_single_href()
                dev_data['sensors'].append(sensor_data)
                sensor_data['data'] = []
        return cls.render_response(response, request)

    @classmethod
    def urls(cls):
        base_patterns = super(SiteResource, cls).urls()
        base_patterns.append(
            url(r'^(\d+)/summary$', cls.site_summary_view,
                name='site-summary'))
        return base_patterns


class ApiRootResource(Resource):

    def __init__(self, request):
        self._request = request

    def serialize(self):
        data = {
            '_links': {
                'self': {'href': full_reverse('api-root', self._request)},
                'curies': CHAIN_CURIES,
                'ch:sites': {
                    'title': 'Sites',
                    'href': full_reverse('sites-list', self._request)
                }
            }
        }
        return data

    @classmethod
    def single_view(cls, request):
        resource = cls(request=request)
        response_data = resource.serialize()
        return cls.render_response(response_data, request)


# URL Setup:

urls = patterns(
    '',
    url(r'^/?$', ApiRootResource.single_view, name='api-root')
)

# add additional URLS to account for the rename of sensor to scalarsensor.
# unfortunately we can't use redirects in case clients are POSTing to outdated
# URLs. If we WERE redirecting, we would use RedirectView.as_view()
#
# put these first so they are overridden by the later ones, particularly when
# doing URL reverse lookup.

urls += patterns('',
                 url("^sensordata/", include(ScalarSensorDataResource.urls())),
                 url("^sensor/", include(ScalarSensorResource.urls())),
                 )

resources = [
    ScalarSensorDataResource,
    AggregateScalarSensorDataResource,
    ScalarSensorResource,
    PresenceDataResource,
    PresenceSensorResource,
    PersonResource,
    MixedSensorResource,
    DeviceResource,
    SiteResource]

for resource in resources:
    new_url = url("^%s/" % resource.resource_name, include(resource.urls()))
    urls += patterns('', new_url)
    register_resource(resource)
