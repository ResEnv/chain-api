from chain.core.api import Resource, ResourceField, CollectionField
from chain.core.api import full_reverse
from chain.core.api import CHAIN_CURIES
from chain.core.models import Site, Device, Sensor, ScalarData
from django.conf.urls import include, patterns, url
from django.utils import timezone
from datetime import timedelta


class SensorDataResource(Resource):
    model = ScalarData
    display_field = 'timestamp'
    resource_name = 'data'
    resource_type = 'data'
    model_fields = ['timestamp', 'value']
    required_fields = ['timestamp', 'value']
    queryset = ScalarData.objects
    page_size = 500

    def __init__(self, *args, **kwargs):
        super(SensorDataResource, self).__init__(*args, **kwargs)
        if 'queryset' in kwargs:
            if 'offset' not in kwargs or kwargs['offset'] is None:
                # we want to default to the last page, not the first page
                total_count = self.get_total_count()
                self._offset = max(total_count - self._limit, 0)

    def serialize_list(self, embed, cache):
        '''a "list" of SensorData resources is actually represented
        as a single resource with a list of data points'''
        if not embed:
            return super(SensorDataResource, self).serialize_list(embed, cache)

        href = self.get_list_href()

        serialized_data = {
            '_links': {
                'self': {'href': href},
                'curies': CHAIN_CURIES,
                'createForm': {
                    'href': self.get_create_href(),
                    'title': 'Add Data'
                }
            },
            'totalCount': self.get_total_count(),
            'dataType': 'float'
        }
        objs = self._queryset.filter(**self._filters).order_by('timestamp')
        objs = objs[self._offset:self._offset + self._limit]
        serialized_data['data'] = [{
            'value': obj.value,
            'timestamp': obj.timestamp.isoformat()}
            for obj in objs]
        serialized_data = self.add_page_links(serialized_data, href)
        return serialized_data


class SensorResource(Resource):

    model = Sensor
    display_field = 'metric'
    resource_name = 'sensors'
    resource_type = 'sensor'
    required_fields = ['metric', 'unit']

    # for now, name is hardcoded as the only attribute of metric and unit
    stub_fields = {'metric': 'name', 'unit': 'name'}
    queryset = Sensor.objects
    related_fields = {
        'ch:dataHistory': CollectionField(SensorDataResource,
                                          reverse_name='sensor'),
        'ch:device': ResourceField('chain.core.resources.DeviceResource',
                                   'device')
    }

    def serialize_single(self, embed, cache, *args, **kwargs):
        data = super(SensorResource, self).serialize_single(embed, cache,
                                                            *args, **kwargs)
        if embed:
            data['dataType'] = 'float'
            last_data = self._obj.scalar_data.order_by(
                'timestamp').reverse()[:1]
            if last_data:
                data['value'] = last_data[0].value
                data['updated'] = last_data[0].timestamp.isoformat()
        return data


class DeviceResource(Resource):

    model = Device
    display_field = 'name'
    resource_name = 'devices'
    resource_type = 'device'
    required_fields = ['name']
    model_fields = ['name', 'description', 'building', 'floor', 'room']
    related_fields = {
        'ch:sensors': CollectionField(SensorResource,
                                      reverse_name='device'),
        'ch:site': ResourceField('chain.core.resources.SiteResource', 'site')
    }
    queryset = Device.objects


class SiteResource(Resource):

    model = Site

    # TODO _href should be the external URL if present

    resource_name = 'sites'
    resource_type = 'site'
    display_field = 'name'
    model_fields = ['name']
    required_fields = ['name']
    related_fields = {
        'ch:devices': CollectionField(DeviceResource, reverse_name='site')
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

    @classmethod
    def get_schema(cls):
        schema = super(SiteResource, cls).get_schema()
        schema['properties']['rawZMQStream'] = {
            'type': 'string',
            'format': 'uri',
            'title': 'rawZMQStream'
        }
        return schema

    @classmethod
    def site_summary_view(cls, request, id):
        time_begin = timezone.now() - timedelta(hours=2)
        #filters = request.GET.dict()
        devices = Device.objects.filter(site_id=id).select_related(
            'sensors',
            'sensors__metric',
            'sensors__unit')
        sensor_data = ScalarData.objects.filter(sensor__device__site_id=id,
                                                timestamp__gt=time_begin)
        response = {
            '_links': {
                'self': {'href': full_reverse('site-summary', request,
                                              args=(id,))},
            },
            'devices': []
        }
        sensor_hash = {}
        for device in devices:
            dev_resource = DeviceResource(
                obj=device, request=request).serialize(rels=False)
            response['devices'].append(dev_resource)
            dev_resource['sensors'] = []
            for sensor in device.sensors.all():
                sensor_resource = SensorResource(
                    obj=sensor, request=request).serialize(rels=False)
                dev_resource['sensors'].append(sensor_resource)
                sensor_resource['data'] = []
                sensor_hash[sensor.id] = sensor_resource

        for data in sensor_data:
            data_resource = SensorDataResource(
                obj=data, request=request).serialize(rels=False)
            sensor_hash[data.sensor_id]['data'].append(data_resource)
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


urls = patterns(
    '',
    url(r'^/$', ApiRootResource.single_view, name='api-root'),
    url(r'^$', ApiRootResource.single_view, name='api-root'),
    url(r'^sites/', include(SiteResource.urls())),
    url(r'^devices/', include(DeviceResource.urls())),
    url(r'^sensors/', include(SensorResource.urls())),
    url(r'^sensordata/', include(SensorDataResource.urls())),
)
