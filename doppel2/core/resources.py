from doppel2.core.api import Resource, ResourceField, CollectionField
from doppel2.core.api import full_reverse
from doppel2.core.models import Site, Device, Sensor, ScalarData
from django.conf.urls import include, patterns, url
from django.http import HttpResponse
import json


class SensorDataResource(Resource):
    model = ScalarData
    resource_name = 'data'
    resource_type = 'data'
    model_fields = ['timestamp', 'value']
    related_fields = {'sensor':
                      ResourceField('doppel2.core.resources.SensorResource',
                                    'sensor')}
    queryset = ScalarData.objects


class SensorResource(Resource):

    model = Sensor
    resource_name = 'sensors'
    resource_type = 'sensor'

    # for now, name is hardcoded as the only attribute of metric and unit
    callback_fields = ['timestamp', 'value']
    stub_fields = {'metric': 'name', 'unit': 'name'}
    queryset = Sensor.objects
    related_fields = {
        'history': CollectionField(SensorDataResource,
                                   reverse_name='sensor'),
        'device': ResourceField('doppel2.core.resources.DeviceResource',
                                'device')
    }


class DeviceResource(Resource):

    model = Device
    resource_name = 'devices'
    resource_type = 'device'

    # TODO: add site linked field

    model_fields = ['name', 'description', 'building', 'floor', 'room']
    related_fields = {
        'sensors': CollectionField(SensorResource,
                                   reverse_name='device', embed=True),
        'site': ResourceField('doppel2.core.resources.SiteResource', 'site')
    }
    queryset = Device.objects


class SiteResource(Resource):

    model = Site

    # TODO _href should be the external URL if present

    resource_name = 'sites'
    resource_type = 'site'
    model_fields = ['name', 'latitude', 'longitude']
    related_fields = {
        'devices': CollectionField(DeviceResource, reverse_name='site',
                                   embed=False)
    }
    queryset = Site.objects


class ApiRootResource:

    def __init__(self, request):
        self._request = request

    def serialize(self):
        data = {'_href': full_reverse('api-root', self._request),
                '_type': 'api-root',
                'sites': SiteResource(queryset=Site.objects,
                request=self._request).serialize()}
        return data

    @classmethod
    def single_view(cls, request):
        resource = cls(request=request)
        response_data = json.dumps(resource.serialize())
        return HttpResponse(response_data)


urls = patterns(
    '',
    url(r'^$', ApiRootResource.single_view, name='api-root'),
    url(r'^sites/', include(SiteResource.urls())),
    url(r'^devices/', include(DeviceResource.urls())),
    url(r'^sensors/', include(SensorResource.urls())),
    url(r'^sensordata/', include(SensorDataResource.urls())),
)
