#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from django.conf.urls import patterns, url
from django.db import models
import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from datetime import datetime
from jinja2 import Environment, PackageLoader
from urlparse import urlparse, urlunparse, parse_qs
from urllib import urlencode
from chain.core.models import GeoLocation
from chain.settings import WEBSOCKET_PATH, WEBSOCKET_HOST, \
    ZMQ_PASSTHROUGH_URL_PULL
import zmq
import re


def capitalize(word):
    return word[0].upper() + word[1:]


def schema_type_from_model_field(field):
    field_class = field.__class__
    if field_class == models.FloatField:
        return 'number', None
    elif field_class in [models.CharField, models.TextField]:
        return 'string', None
    elif field_class == models.DateTimeField:
        return 'string', 'date-time'
    elif field_class == models.BooleanField:
        return 'boolean', None
    elif field_class == models.ForeignKey:
        return 'string', 'url'
    else:
        raise NotImplementedError('Field type %s not recognized' % field_class)


# TODO: this should get the URL dynamically
CHAIN_CURIES = [{
    'name': 'ch',
    'href': 'http://chain-api.media.mit.edu/rels/{rel}',
    'templated': True
}]

HTTP_STATUS_SUCCESS = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_NOT_ACCEPTABLE = 406
HTTP_STATUS_BAD_REQUEST = 400

jinja_env = Environment(loader=PackageLoader('chain.core', 'templates'))

# Set up ZMQ feed for realtime clients
zmq_ctx = zmq.Context()
zmq_socket = zmq_ctx.socket(zmq.PUSH)
zmq_socket.connect(ZMQ_PASSTHROUGH_URL_PULL)


def full_reverse(view_name, request, *args, **kwargs):
    partial_reverse = reverse(view_name, *args, **kwargs)
    return request.build_absolute_uri(partial_reverse)


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


class CollectionField(object):

    '''A Collection field is a field on a resource that points to a child
    collection, e.g. an Author resource might have a 'books' field that is a
    collection of all the books by that author. By default the serialized data
    will only have a link to the child collection, but by setting embed=True
    you can actually embed the full collection inside the parent object.'''

    def __init__(self, child_resource_class, reverse_name, embed=False):
        self._reverse_name = reverse_name
        self._child_resource_class = child_resource_class
        self._embed = embed

    def serialize(self, parent, request, cache):
        queryset = self._child_resource_class.queryset

        # generate a filter on the child collection so we get the actual
        # children, and not all the resources

        parent_filter = {self._reverse_name + '_id': parent._obj.id}
        return self._child_resource_class(queryset=queryset, request=request,
                                          filters=parent_filter).serialize(
                                              embed=self._embed, cache=cache)


class ResourceField(object):

    '''Describes a related single resource field, e.g. a Book resource might
    have an 'author' field that links (or embeds) the author resource'''

    def __init__(self, related_resource_class, parent_field_name, embed=False):
        self._related_resource_class = related_resource_class
        self._parent_field_name = parent_field_name
        self._embed = embed

    def serialize(self, parent, request, cache):
        self._related_resource_class = unlazy(self._related_resource_class)
        # TODO: shouldn't be reaching directly into parent._obj! refactor
        obj = getattr(parent._obj, self._parent_field_name)
        return self._related_resource_class(obj=obj,
                                            request=request).serialize(
                                                embed=self._embed, cache=cache)


def serialize_geo_location(loc):
    return {
        'elevation': loc.elevation,
        'latitude': loc.latitude,
        'longitude': loc.longitude
    }


def get_filtered_fields(filters):
    filtered_fields = set()
    regex_id = r'(.*)_id$'
    for filter in filters:
        match = re.search(regex_id, filter)
        if match is not None:
            filtered_fields.add(match.group(1))
    return filtered_fields


class Resource(object):
    model = None
    resource_name = None
    resource_type = None
    queryset = None
    model_fields = []
    related_fields = {}
    stub_fields = {}
    required_fields = []
    page_size = 30

    def __init__(self, obj=None, queryset=None, data=None, request=None,
                 filters=None, limit=None, offset=None):
        if len([arg for arg in [obj, queryset, data] if arg]) != 1:
            logging.error(
                'Exactly 1 object, queryset, or primitive data is required')
        self._queryset = queryset
        self._data = data
        self._obj = obj
        self._filters = filters or {}
        self._request = request
        self._limit = limit or self.page_size
        self._offset = offset or 0

    def serialize_single(self, embed=True, cache=None, rels=True):
        '''Serializes this object, assuming that there is a single instance to
        be serialized. Note that this only gets called from the top-level
        serialize() method, which handles checking whether we're in the
        cache'''
        data = {}
        if not embed:
            # this is just a link, don't embed the full object
            data['href'] = self.get_single_href()
            title = self.display_field
            if title in self.model_fields:
                data['title'] = self.serialize_field(getattr(self._obj, title))
            elif title in self.stub_fields.keys():
                stub_data = getattr(self._obj, title)
                data['title'] = getattr(stub_data, self.stub_fields[title])
            else:
                raise NotImplementedError(
                    'display_field must be a model field or stub field')
            return data
        if rels:
            data['_links'] = {
                'self': {
                    'href': self.get_single_href(),
                },
                'editForm': {
                    'href': self.get_edit_href(),
                    'title': 'Edit %s' % capitalize(self.resource_type)
                },
                'ch:websocketStream': {
                    'href': self.get_websocket_href(),
                    'title': 'Websocket Stream'
                },
                'curies': CHAIN_CURIES
            }
            for field_name, collection in self.related_fields.items():
                # collection is a CollectionField or ResourceField here
                data['_links'][field_name] = collection.serialize(
                    self, self._request, cache)

        for field_name in self.model_fields:
            data[field_name] = self.serialize_field(
                getattr(self._obj, field_name))
        for stub in self.stub_fields.keys():
            stub_data = getattr(self._obj, stub)
            data[stub] = getattr(stub_data, self.stub_fields[stub])
        # check to see whether this object has a geolocation
        try:
            loc = self._obj.geo_location
            if loc is not None:
                data['geoLocation'] = serialize_geo_location(loc)
        except AttributeError:
            # guess this model doesn't support geo_location
            pass
        return data

    def serialize_stream(self):
        '''By default resources are serialized for streams in their normal
        format. Resource subclasses can override this if they want a different
        representation for streaming'''
        return self.serialize()

    def serialize_field(self, field_value):
        '''some fields require special handling to be serialized. Handle
        that here'''
        if isinstance(field_value, datetime):
            return field_value.isoformat()
        return field_value

    def get_total_count(self):
        '''Gets the total number of objects in the queryset for this request,
        ignoring pagination. We cache the result because this query is actually
        pretty slow.'''
        try:
            return self._total_count
        except AttributeError:
            pass
        qs = self._queryset
        if self._filters:
            qs = qs.filter(**self._filters)
        self._total_count = qs.count()
        return self._total_count

    def get_queryset(self):
        '''Returns the queryset resulting from this request, including
        all filtering, and pagination'''
        queryset = self._queryset.filter(**self._filters)
        return queryset[self._offset:self._offset + self._limit]

    def get_single_href(self):
        '''Gives the URL for this single element, assuming we have an
        object'''
        return full_reverse(self.resource_name + '-single',
                            self._request, args=(self._obj.id,))

    def get_edit_href(self):
        '''Gives the URL for this single element, assuming we have an
        object'''
        return full_reverse(self.resource_name + '-edit',
                            self._request, args=(self._obj.id,))

    def update_href(self, href, **kwargs):
        '''Takes a link href as a string, and updates the query string with the
        given query parameters'''
        scheme, netloc, path, params, query, fragment = urlparse(href)
        # Note that values from parse_qs are actually lists in order to
        # accomodate possible duplicate keys. make sure you encode with
        # doseq=True
        query_params = parse_qs(query)
        query_params.update(kwargs)
        query = urlencode(query_params, doseq=True)
        return urlunparse((scheme, netloc, path, params, query, fragment))

    def get_websocket_href(self):
        '''Gives the URL for the websockets stream that provides updates
        on this resource as well as nested resources.'''
        try:
            hostname = WEBSOCKET_HOST or self._request.META['HTTP_HOST']
        except KeyError:
            # TODO: raise an error that gets handled and returns a 400 response
            raise

        return "ws://%s/%s%s-%d" % (hostname,
                                    WEBSOCKET_PATH,
                                    self.resource_type, self._obj.id)

    def get_list_href(self):
        '''Gives the URL for this resource, including any filtering
        and pagination query parameters'''
        # TODO: use this for single views as well
        href = full_reverse(self.resource_name + '-list', self._request)
        query_params = self._filters.items()
        href += '?' + urlencode(query_params)
        return href

    def get_create_href(self):
        href = full_reverse(self.resource_name + '-create', self._request)
        query_params = self._filters.items()
        if query_params:
            href += '?' + urlencode(query_params)
        return href

    def get_tags(self):
        '''Returns a list of tags applicable to this instance of the resource.
        this gets called on a resource after POSTing (either creating a new one
        or editing an existing one'''
        return []

    def add_page_links(self, data, href):
        offset = self._offset
        limit = self._limit
        total_count = self.get_total_count()
        if offset > 0:
            # make previous link
            prev_offset = offset - limit if offset - limit > 0 else 0
            data['_links']['previous'] = {
                'href': self.update_href(href,
                                         offset=prev_offset, limit=limit),
                'title': '%d through %d' % (
                    prev_offset, prev_offset + limit - 1),
            }
            # make first link
            data['_links']['first'] = {
                'href': self.update_href(href, offset=0, limit=limit),
                'title': '0 through %d' % (limit - 1),
            }

        if offset + limit < total_count:
            # make next link
            if offset + 2 * limit < total_count:
                next_page_end = offset + 2 * limit
            else:
                next_page_end = total_count
            data['_links']['next'] = {
                'href': self.update_href(href,
                                         offset=(offset + limit),
                                         limit=limit),
                'title': '%d through %d' % (
                    offset + limit, next_page_end - 1),
            }
            last_page_start = int(total_count / limit) * limit
            data['_links']['last'] = {
                'href': self.update_href(href,
                                         offset=last_page_start,
                                         limit=limit),
                'title': '%d through %d' % (
                    last_page_start, total_count - 1),
            }
        return data

    def serialize_list(self, embed, cache):
        '''Serializes this object, assuming that there is a queryset that needs
        to be serialized as a collection'''

        href = self.get_list_href()

        if not embed:
            # the actual items aren't embedded, we're just providing a link
            # to this collection
            data = {
                'href': href,
                'title': capitalize(self.resource_name)
            }
            return data

        serialized_data = {
            '_links': {
                'self': {'href': href},
                'curies': CHAIN_CURIES,
                'createForm': {
                    'href': self.get_create_href(),
                    'title': 'Create %s' % capitalize(self.resource_type)
                }
            },
            'totalCount': self.get_total_count()
        }
        queryset = self.get_queryset()
        serialized_data['_links']['items'] = [
            self.__class__(obj=obj, request=self._request).
            serialize(cache=cache, embed=False) for obj in queryset]

        serialized_data = self.add_page_links(serialized_data, href)
        return serialized_data

    def serialize(self, embed=True, cache=None, *args, **kwargs):
        '''Serializes this instance into a dictionary that can be rendered'''
        if cache is None:
            cache = {}

        # first check to see if we're already in the cache, in which case we
        # can just return what was already calculated. Note that the key for
        # the cache includes whether we're embedded. This means that the same
        # object may be in the cache in both the embedded and non-embedded
        # forms, but that is likely a small price to pay for simplicity

        if self._queryset:
            # we don't currently handle cacheing whole collection lists.
            self._data = self.serialize_list(embed, cache,
                                             *args, **kwargs)

        elif self._obj:
            if (self._obj.__class__, self._obj.id, embed) in cache:
                return cache[(self._obj.__class__, self._obj.id, embed)]
            else:
                self._data = self.serialize_single(embed, cache,
                                                   *args, **kwargs)
                cache[(self._obj.__class__, self._obj.id, embed)] = self._data

        return self._data

    def stub_object_finding(self, obj, field_name, field_value):
        '''Looks up the matching related field, and creates it if it doesn't
        already exist.'''
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

    @classmethod
    def model_has_field(cls, field_name):
        try:
            cls.model._meta.get_field_by_name(field_name)
            return True
        except models.FieldDoesNotExist:
            return False

    @classmethod
    def sanitize_field_value(cls, field_name, value):
        '''Converts the given value to the correct python tyhttp://localhost:8080/people/1pe, for instance if
        the field is supposed to be a float field and the string "23" is given,
        it will be converted to 23.0

        NOTE - this currently only works for vanilla model fields, which serves
        our purposes for now'''
        field = cls.model._meta.get_field_by_name(field_name)[0]
        field_class = field.__class__
        if field_class == models.ForeignKey:
            lookup = lookup_associated_model_object(value)
            if lookup is None:
                raise BadRequestException(
                    "The url to the given resource does not exist.")
            return lookup
        return field.to_python(value)

    def deserialize(self):
        '''Deserializes this instance and returns the object representation'''

        if self._obj:
            return self._obj
        new_obj_data = {}

        filtered_fields = get_filtered_fields(self._filters)

        # take the intersection of the fields given and the fields in
        # self.model_fields

        for field_name in [f for f in self.model_fields
                           if f in self._data]:
            if field_name in filtered_fields:
                continue
            value = self.sanitize_field_value(field_name,
                                              self._data[field_name])
            new_obj_data[field_name] = value

        for stub_field_name in self.stub_fields.keys():
            new_obj_data[stub_field_name] = self.stub_object_finding(
                new_obj_data, stub_field_name, self._data[stub_field_name])
        if self.model_has_field('geo_location') and \
                'geoLocation' in self._data:
            dataloc = self._data['geoLocation']
            loc = GeoLocation(elevation=dataloc.get('elevation', None),
                              latitude=dataloc['latitude'],
                              longitude=dataloc['longitude'])
            loc.save()
            new_obj_data['geo_location'] = loc
        # the query string may contain more object data, for instance if
        # we're posting to a child collection resource

        new_obj_data.update(self._filters)
        self._obj = self.model(**new_obj_data)
        return self._obj

    def update(self, data):
        '''Updates this resource given the data, which is expected to be a dict
        in the format given by this resource's schema'''
        for k, v in data.iteritems():
            if k in self.model_fields:
                setattr(self._obj, k, v)
            elif k in self.stub_fields:
                setattr(self._obj, k,
                        self.stub_object_finding(self._obj, k, v))
            elif k == 'geoLocation':
                loc = self._obj.geo_location
                if loc is None:
                    loc = GeoLocation(elevation=v.get('elevation', None),
                                      latitude=v['latitude'],
                                      longitude=v['longitude'])
                    loc.save()
                    self._obj.geo_location = loc
                else:
                    for field, value in v.iteritems():
                        setattr(loc, field, value)
                    loc.save()
        self._obj.save()

    def save(self):
        if not self._obj:
            # here we're using the side-effect of serialization that we save
            # the object after deserialization
            self.deserialize()
        self._obj.save()

    def get_filled_schema(self):
        '''Returns a schema dict with default values filled from the object's
        values'''
        schema = self.get_schema()
        schema['title'] = 'Edit ' + capitalize(self.resource_type)
        props = schema['properties']
        for field in self.model_fields:
            props[field]['default'] = self.serialize_field(
                getattr(self._obj, field))
        for stub in self.stub_fields.keys():
            stub_data = getattr(self._obj, stub)
            props[stub]['default'] = getattr(stub_data, self.stub_fields[stub])
        try:
            geo_loc = self._obj.geo_location
        except AttributeError:
            geo_loc = None
        if geo_loc is not None:
            props['geoLocation']['properties']['latitude']['default'] = \
                geo_loc.latitude
            props['geoLocation']['properties']['longitude']['default'] = \
                geo_loc.longitude
            elevation = geo_loc.elevation
            if elevation is not None:
                props['geoLocation']['properties']['elevation']['default'] = \
                    elevation

        return schema

    @classmethod
    def render_response(cls, data, request, status=None):
        # TODO: there's got to be a more robust library to parse accept headers
        if 'HTTP_ACCEPT' not in request.META:
            request.META['HTTP_ACCEPT'] = 'application/json'
        for accept in request.META['HTTP_ACCEPT'].split(','):
            accept = accept.strip()
            # first handle possible wildcards
            if accept in ['*/*', 'application/*', '*/json', '*/hal+json']:
                accept = 'application/hal+json'
            if accept in ['application/hal+json', 'application/json']:
                return HttpResponse(json.dumps(data), status=status,
                                    content_type=accept)
            elif accept == 'text/html':
                context = {'resource': data,
                           'json_str': json.dumps(data, indent=2)}
                template = jinja_env.get_template('resource.html')
                return HttpResponse(template.render(**context),
                                    status=status,
                                    content_type=accept)
        err_data = {
            'message': "MIME type not supported.\ Try text/html, \
            application/json, or application/hal+json",
        }
        return HttpResponse(json.dumps(err_data),
                            status=HTTP_STATUS_NOT_ACCEPTABLE,
                            content_type="application/hal+json")

    @classmethod
    @csrf_exempt
    def list_view(cls, request):
        offset = None
        limit = None
        filters = request.GET.dict()
        if 'offset' in filters:
            try:
                offset = int(filters.pop('offset'))
            except ValueError:
                pass
        if 'limit' in filters:
            try:
                limit = int(filters.pop('limit'))
            except ValueError:
                pass
        try:
            response_data = cls(queryset=cls.queryset, request=request,
                                filters=filters, offset=offset,
                                limit=limit).serialize()
            return cls.render_response(response_data, request)
        except BadRequestException as e:
            return render_error(HTTP_STATUS_BAD_REQUEST, e.message, request)

    @classmethod
    def get_field_schema_type(cls, field_name):
        '''Returns the type string and format for a given field name, usable in
        the schema definition. Format may be None'''
        if field_name in cls.model_fields:
            field = cls.model._meta.get_field_by_name(field_name)[0]
        elif field_name in cls.stub_fields.keys():
            stub_data = cls.model._meta.get_field_by_name(field_name)[0]
            field = stub_data.rel.to._meta.get_field_by_name(
                cls.stub_fields[field_name])[0]
        else:
            raise NotImplementedError(
                "tried to look up field %s but didn't know where" % field_name)
        # returns a (type, format) tuple
        return schema_type_from_model_field(field)

    @classmethod
    def get_schema(cls, filters=None):
        '''Returns the JSON schema for this resource as a dictionary.
        Subclasses should override this method'''
        if filters is None:
            filters = {}
        filtered_fields = get_filtered_fields(filters)
        schema = {
            'type': 'object',
            'title': 'Create ' +
            capitalize(
                cls.resource_type),
            'properties': {},
            'required': [
                field for field in cls.required_fields if field not in filtered_fields]}
        for field_name in cls.model_fields + cls.stub_fields.keys():
            if field_name in filtered_fields:
                continue
            sch_type, sch_format = cls.get_field_schema_type(field_name)
            schema['properties'][field_name] = {
                'type': sch_type,
                'title': field_name
            }
            if sch_format:
                schema['properties'][field_name]['format'] = sch_format
            # don't allow empty strings in required fields
            if field_name in cls.required_fields and sch_type == 'string':
                schema['properties'][field_name]['minLength'] = 1
        if cls.model_has_field('geo_location'):
            schema['properties']['geoLocation'] = {
                'type': 'object',
                'title': 'geoLocation',
                'properties': {
                    'latitude': {'type': 'number', 'title': 'latitude'},
                    'longitude': {'type': 'number', 'title': 'longitude'},
                    'elevation': {'type': 'number', 'title': 'elevation'}
                },
                'required': ['latitude', 'longitude']
            }
        return schema

    @classmethod
    def single_view(cls, request, id):
        response_data = cls(obj=cls.queryset.get(id=id),
                            request=request).serialize()
        return cls.render_response(response_data, request)

    @classmethod
    @csrf_exempt
    def edit_view(cls, request, id):
        if request.method == 'GET':
            resource = cls(obj=cls.queryset.get(id=id), request=request)
            schema = resource.get_filled_schema()
            return cls.render_response(schema, request)

        elif request.method == 'POST':
            # if not request.user.is_authenticated():
            #    return render_401(request)
            resource = cls(obj=cls.queryset.get(id=id), request=request)
            try:
                data = json.loads(request.body)
            except ValueError:
                return render_error(
                    HTTP_STATUS_BAD_REQUEST,
                    "The edit operation could not be performed because the data provided in the request body cannot be parsed as legal JSON.",
                    request)
            try:
                resource.update(data)
            except IntegrityError:
                return render_error(
                    400, 'Error storing object. Either required fields are '
                    'missing data or a matching object already exists',
                    request)
            response_data = resource.serialize()
            # push to the appropriate streams
            tags = resource.get_tags()
            if tags:
                stream_data = json.dumps(resource.serialize_stream())
            for tag in tags:
                zmq_socket.send_string(tag + ' ' + stream_data)
            return cls.render_response(response_data, request)

    @classmethod
    @csrf_exempt
    def create_view(cls, request):
        if request.method == 'GET':
            schema = cls.get_schema(request.GET.dict())
            return cls.render_response(schema, request)

        elif request.method == 'POST':
            # if not request.user.is_authenticated():
            #    return render_401(request)
            try:
                data = json.loads(request.body)
            except ValueError:
                return render_error(
                    HTTP_STATUS_BAD_REQUEST,
                    "The create operation could not be performed because the data provided in the request body cannot be parsed as legal JSON.",
                    request)
            if isinstance(data, list):
                return cls.create_list(data, request)
            else:
                return cls.create_single(data, request)

    @classmethod
    def create_single(cls, data, request):
        obj_params = request.GET.dict()
        new_resource = cls(data=data, request=request, filters=obj_params)
        try:
            new_resource.save()
        except IntegrityError:
            return render_error(
                400, 'Error storing object. Either required fields are '
                'missing data or a matching object already exists',
                request)
        response_data = new_resource.serialize()
        tags = new_resource.get_tags()
        if tags:
            stream_data = json.dumps(new_resource.serialize_stream())
        for tag in tags:
            zmq_socket.send_string(tag + ' ' + stream_data)
        return cls.render_response(response_data, request,
                                   status=HTTP_STATUS_CREATED)

    @classmethod
    def create_list(cls, data, request):
        response_data = []
        for item in data:
            obj_params = request.GET.dict()
            new_resource = cls(data=item, request=request, filters=obj_params)
            try:
                new_resource.save()
            except IntegrityError:
                return render_error(
                    400, 'Error storing object. Either required fields are '
                    'missing data or a matching object already exists',
                    request)
            response_data.append(new_resource.serialize())
            tags = new_resource.get_tags()
            if tags:
                stream_data = json.dumps(new_resource.serialize_stream())
            for tag in tags:
                zmq_socket.send_string(tag + ' ' + stream_data)
        return cls.render_response(response_data, request,
                                   status=HTTP_STATUS_CREATED)

    @classmethod
    def urls(cls):
        base_name = cls.resource_name
        return patterns('',
                        url(r'^$',
                            cls.list_view, name=base_name + '-list'),
                        url(r'^(\d+)$',
                            cls.single_view, name=base_name + '-single'),
                        url(r'^(\d+)/edit$',
                            cls.edit_view, name=base_name + '-edit'),
                        url(r'^create$',
                            cls.create_view, name=base_name + '-create'))

# Resource URL Setup and Lookup:

url_resource_map = {}

resource_type_pattern = re.compile("^(?:https?://)?[^/]*/([^/]+)")


def lookup_associated_resource_type(url):
    match = resource_type_pattern.match(url)
    if match is None:
        return None
    else:
        return url_resource_map.get(match.group(1), None)


def lookup_associated_model(url):
    res_type = lookup_associated_resource_type(url)
    if res_type is None:
        return None
    else:
        return res_type.model

resource_instance_pattern = re.compile("^(?:https?://)?[^/]*/([^/]+)/(\d+)")


def lookup_associated_model_object(url):
    match = resource_instance_pattern.match(url)
    if match is None:
        return None
    resc_type = url_resource_map.get(match.group(1), None)
    if resc_type is None:
        return None
    model_type = resc_type.model
    if model_type is None:
        return None
    instances = model_type.objects.filter(id=int(match.group(2)))
    if len(instances) == 0:
        return None
    return instances[0]


def register_resource(resource):
    url_resource_map[resource.resource_name] = resource


# Error Handling:

class BadRequestException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "[Bad Request: " + repr(self.message) + "]"


def render_error(status, msg, request):
    err_data = {
        'status': status,
        'message': msg,
    }
    return HttpResponse(json.dumps(err_data), status=status,
                        content_type="application/json")


# def render_401(request):
#    err_data = {
#        'status': 401,
#        'message': 'Unauthorized - Login Required',
#    }
#    response = HttpResponse(json.dumps(err_data), status=401,
#                            content_type="application/json")
#    response['WWW-Authenticate'] = 'Basic Realm="ChainAPI"'
# import pdb; pdb.set_trace()
#    return response


def handle500(request):
    return render_error(
        500,
        "I'm sorry, you broke the server. Those responsible have been sacked.",
        request)


def handle404(request):
    return render_error(HTTP_STATUS_NOT_FOUND, 'Resource not found', request)
