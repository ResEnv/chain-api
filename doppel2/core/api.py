import logging
from doppel2.core.models import Site, Device
from django.conf.urls import patterns, url, include
import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse


def full_reverse(view_name, request, *args, **kwargs):
    partial_reverse = reverse(view_name, *args, **kwargs)
    return request.build_absolute_uri(partial_reverse)


class EmbeddedCollectionField:
    def __init__(self, child_resource_class, reverse):
        self._reverse = reverse
        self._child_resource_class = child_resource_class

    def serialize(self, parent):
        pass
#        base_queryset = self._child_resource_class.queryset
#        return self._child_resource_class()


class ResourceFactory:
    def __init__(self, resource_class):
        base_name = resource_class.resource_name
        self.urls = patterns(
            '',
            url(r'^$', resource_class.list_view,
                name=base_name + '-list'),
            url(r'^(\d+)$', resource_class.single_view,
                name=base_name + '-single')
        )


class Resource:
    resource_name = None
    resource_type = None
    queryset = None
    model_fields = []
    child_collections = {}

    def __init__(self, obj=None, queryset=None, data=None):
        if len([arg for arg in [obj, queryset, data] if arg]) != 1:
            logging.error(
                'Exactly 1 object, queryset, or primitive data is required')
        self._queryset = queryset
        self._data = data
        self._obj = obj

    def serialize_single(self, request):
        '''Serializes this object, assuming that there is a single instance to
        be serialized'''
        data = {
            '_href': full_reverse(self.resource_name + '-single', request,
                                  args=(self._obj.id,)),
            '_type': self.resource_type,
        }
        for field in self.model_fields:
            data[field] = getattr(self._obj, field)
        for field, resource_class in self.child_collections.items():
            data[field] = resource_class(
                queryset=getattr(self._obj, field)).serialize(request)

        return data

    def serialize_list(self, request, filters=None):
        '''Serializes this object, assuming that there is a queryset that needs
        to be serialized as a collection'''

        filters = filters or {}

        return {
            '_href': full_reverse(self.resource_name + '-list', request),
            '_type': 'resource-list',
            'data': [self.__class__(obj=obj).serialize(request)
                     for obj in self.filter_queryset(request)]
        }

    def filter_queryset(self, request):
        '''Filters our queryset based on the passed parameters. Currently
        we're not doing any error checking on these'''
        #TODO: do some error checking here
        return self._queryset.filter(**request.GET.dict())

    def serialize(self, request):
        '''Serializes this instance into a dictionary that can be rendered'''
        if not self._data:
            if self._queryset:
                self._data = self.serialize_list(request)
            elif self._obj:
                self._data = self.serialize_single(request)
        return self._data

    @classmethod
    def list_view(cls, request):
        response_data = cls(queryset=cls.queryset).serialize(request)
        return HttpResponse(json.dumps(response_data))

    @classmethod
    def single_view(cls, request, id):
        response_data = cls(
            obj=cls.queryset.get(id=id)).serialize(request)
        return HttpResponse(json.dumps(response_data))


class DeviceResource(Resource):
    resource_name = 'devices'
    resource_type = 'device'
    #TODO: add site linked field
    model_fields = ['name', 'description', 'building', 'floor', 'room']
    queryset = Device.objects


class SiteResource(Resource):
    #TODO _href should be the external URL if present
    resource_name = 'sites'
    resource_type = 'site'
    model_fields = ['name', 'latitude', 'longitude']
    #child_collections = {'devices': EmbeddedCollectionField(DeviceResource,
    #                                                        reverse='site')}
    child_collections = {'devices': DeviceResource}
    queryset = Site.objects


class ApiRootResource:
    def serialize(self, request):
        data = {
            '_href': full_reverse('api-root', request),
            '_type': 'api-root',
            'sites': SiteResource(queryset=Site.objects).serialize(request),
        }
        return data

    @classmethod
    def single_view(cls, request):
        resource = cls()
        response_data = json.dumps(resource.serialize(request))
        return HttpResponse(response_data)


urls = patterns(
    '',
    url(r'^$', ApiRootResource.single_view, name='api-root'),
    url(r'^sites/', include(ResourceFactory(SiteResource).urls)),
    url(r'^devices/', include(ResourceFactory(DeviceResource).urls)),
)
