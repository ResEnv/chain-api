#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from django.conf.urls import patterns, url
import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from jinja2 import Environment, PackageLoader
import random
import string

HTTP_STATUS_SUCCESS = 200
HTTP_STATUS_CREATED = 201

jinja_env = Environment(loader=PackageLoader('doppel2.core', 'templates'))


def full_reverse(view_name, request, *args, **kwargs):
    partial_reverse = reverse(view_name, *args, **kwargs)
    return request.build_absolute_uri(partial_reverse)


def gen_id(length=16):
    '''Generates a random string usable as DOM element id'''
    return ''.join(random.choice(string.lowercase) for i in range(length))


# store the objects referenced lazily so we only need to use eval() the first
# time
_lazy_refs = {}


def unlazy(given):
    '''Sometimes to break dependency loops we need to give a string
    representation of an object instead of the object itself, especially when
    classes refer to each other. This function will turn the string
    representation into a real object if necessary.

    The given string must be fully namespaced, e.g.
    'myapp.resources.ThingResource'.

    Note - NEVER call this on a string you received from the user'''
    if isinstance(given, str):
        global _lazy_refs
        try:
            return _lazy_refs[given]
        except KeyError:
            # import the parent object's module so that we have the context to
            # find the referenced class
            mod_name = given.split('.')[0]
            mods = {mod_name: __import__(mod_name)}
            _lazy_refs[given] = eval(given, mods)
            return _lazy_refs[given]
    return given


class CollectionField:
    '''A Collection field is a field on a resource that points to a child
    collection, e.g. an Author resource might have a 'books' field that is a
    collection of all the books by that author. By default the serialized data
    will only have a link to the child collection, but by setting embed=True
    you can actually embed the full collection inside the parent object.'''
    def __init__(self, child_resource_class, reverse_name, embed=False):
        self._reverse_name = reverse_name
        self._child_resource_class = child_resource_class
        self._embed = embed

    def serialize(self, parent, request):
        queryset = self._child_resource_class.queryset

        # generate a filter on the child collection so we get the actual
        # children, and not all the resources

        parent_filter = {self._reverse_name + '_id': parent._obj.id}
        return self._child_resource_class(queryset=queryset, request=request,
                                          filters=parent_filter).serialize(
                                              embed=self._embed)


class ResourceField:
    '''Describes a related single resource field, e.g. a Book resource might
    have an 'author' field that links (or embeds) the author resource'''
    def __init__(self, related_resource_class, parent_field_name, embed=False):
        self._related_resource_class = related_resource_class
        self._parent_field_name = parent_field_name
        self._embed = embed

    def serialize(self, parent, request):
        self._related_resource_class = unlazy(self._related_resource_class)
        # TODO: shouldn't be reaching directly into parent._obj! refactor
        obj = getattr(parent._obj, self._parent_field_name)
        return self._related_resource_class(obj=obj,
                                            request=request).serialize(
                                                embed=self._embed)


class Resource:
    #TODO: errors (4xx, 5xx, etc.) should be returned JSON-encoded

    model = None
    resource_name = None
    resource_type = None
    queryset = None
    model_fields = []
    related_fields = {}
    stub_fields = {}
    callback_fields = []

    def __init__(self, obj=None, queryset=None, data=None, request=None,
                 filters=None):
        if len([arg for arg in [obj, queryset, data] if arg]) != 1:
            logging.error(
                'Exactly 1 object, queryset, or primitive data is required')
        self._queryset = queryset
        self._data = data
        self._obj = obj
        self._filters = filters or {}
        self._request = request

    def serialize_single(self, embed):
        '''Serializes this object, assuming that there is a single instance to
        be serialized'''
        data = {
            '_href': full_reverse(self.resource_name + '-single',
                                  self._request, args=(self._obj.id,)),
        }
        disp = self.display_field
        if disp in self.model_fields:
            data['_disp'] = self.serialize_field(getattr(self._obj, disp))
        elif disp in self.stub_fields.keys():
            stub_data = getattr(self._obj, disp)
            data['_disp'] = getattr(stub_data, self.stub_fields[disp])
        else:
            raise NotImplementedError(
                'display_field must be a model field or stub field')
        if not embed:
            return data
        data['_type'] = self.resource_type
        for field_name in self.model_fields:
            data[field_name] = self.serialize_field(
                getattr(self._obj, field_name))
        for field_name, collection in self.related_fields.items():
            # collection is an CollectionField here
            data[field_name] = collection.serialize(self, self._request)
        for stub in self.stub_fields.keys():
            stub_data = getattr(self._obj, stub)
            data[stub] = getattr(stub_data, self.stub_fields[stub])
        return data

    def serialize_field(self, field_value):
        '''some fields require special handling to be serialized. Handle
        that here'''
        if isinstance(field_value, datetime):
            return field_value.isoformat()
        return field_value

    def serialize_list(self, embed):
        '''Serializes this object, assuming that there is a queryset that needs
        to be serialized as a collection'''

        queryset = self._queryset.filter(**self._filters)
        query_string = ''

        if self._filters:
            query_string = "?" + '&'.join(
                ['%s=%s' % (k, v) for (k, v) in self._filters.items()])
        serialized_data = {
            '_href': full_reverse(self.resource_name + '-list',
                                  self._request) + query_string,
            '_disp': self.resource_name,
        }
        if embed:
            serialized_data.update(
                {
                    '_type': 'resource-list',
                    'meta': {'totalCount': len(queryset)},
                    'data': [self.__class__(obj=obj,
                                            request=self._request).serialize()
                             for obj in queryset]
                })
        return serialized_data

    def serialize(self, embed=True):
        '''Serializes this instance into a dictionary that can be rendered'''

        if self._queryset:
            self._data = self.serialize_list(embed)
        elif self._obj:
            self._data = self.serialize_single(embed)
        return self._data

    def stub_object_finding(self, obj, field_name, field_value):
        stub_field = self.stub_fields[field_name]
        field = getattr(self.model, field_name).field
        # so now we have a model we can run queries against
        related_class = field.rel.to

        query_args = {stub_field: field_value}
        try:
            matching_related_obj = related_class.objects.get(**query_args)
        except related_class.DoesNotExist:
            # a matching object doesn't exist, so we'll create it
            # TODO: this will crash if we can't build up an object based on the
            # given data
            matching_related_obj = related_class(**query_args)
            matching_related_obj.save()

        return matching_related_obj

    def deserialize(self):
        '''Deserializes this instance and returns the object representation'''

        if not self._obj:
            new_obj_data = {}

            # take the intersection of the fields given and the fields in
            # self.model_fields

            for field_name in [f for f in self.model_fields
                               if f in self._data]:
                new_obj_data[field_name] = self._data[field_name]

            for stub_field_name in self.stub_fields.keys():
                new_obj_data[stub_field_name] = self.stub_object_finding(
                    new_obj_data, stub_field_name, self._data[stub_field_name])
            # the query string may contain more object data, for instance if
            # we're posting to a child collection resource

            new_obj_data.update(self._filters)
            self._obj = self.model(**new_obj_data)
        return self._obj

    def save(self):
        if not self._obj:

            # here we're using the side-effect of serialization that we save
            # the object after deserialization

            self.deserialize()
        self._obj.save()

    @classmethod
    def render_response(cls, data, request, status=None):
        # TODO: there's got to be a more robust library to parse accept headers
        for accept in request.META['HTTP_ACCEPT'].split(','):
            if accept == 'application/json' or accept == '*/*':
                return HttpResponse(json.dumps(data), status=status,
                                    content_type=accept)
            elif accept == 'text/html':
                context = {'resource': data,
                           'json_str': json.dumps(data, indent=2),
                           'gen_id': gen_id}
                template = jinja_env.get_template('resource.html')
                return HttpResponse(template.render(**context),
                                    status=status,
                                    content_type=accept)
            else:
                raise NotImplementedError("MIME type %s not supported.\
                        Try text/html or application/json" % accept)

    @classmethod
    @csrf_exempt
    def list_view(cls, request):

        if request.method == 'GET':
            filters = request.GET.dict()
            response_data = cls(queryset=cls.queryset, request=request,
                                filters=filters).serialize()
            return cls.render_response(response_data, request)
        elif request.method == 'POST':
            data = json.loads(request.body)
            new_object = cls(data=data, request=request,
                             filters=request.GET.dict())
            new_object.save()
            response_data = new_object.serialize()
            return cls.render_response(response_data, request,
                                       status=HTTP_STATUS_CREATED)

    @classmethod
    def single_view(cls, request, id):
        response_data = cls(obj=cls.queryset.get(id=id),
                            request=request).serialize()
        return cls.render_response(response_data, request)

    @classmethod
    def urls(cls):
        base_name = cls.resource_name
        return patterns('',
                        url(r'^$',
                            cls.list_view, name=base_name + '-list'),
                        url(r'^(\d+)$',
                            cls.single_view, name=base_name + '-single'))
