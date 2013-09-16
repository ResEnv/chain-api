from django.http import HttpResponse
from doppel2.core.models import ScalarData
from django.db.models import Avg
from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse
import json
from datetime import datetime
import dateutil


# for this to work well we'd need to better handle relationships
def _dict_from_obj(obj):
    obj_dict = {}
    for field in obj._meta.fields:
        value = getattr(obj, field.name)
        # datetimes are not directly JSON serializable
        if isinstance(value, datetime):
            value = value.isoformat()
        obj_dict[field.name] = value
    return obj_dict


def api_home(request):
    # define all the api endpoints
    api_endpoints = {
        'scalar_data': reverse(scalar_data),
    }
    return HttpResponse(json.dumps(api_endpoints))


def parse_query(request):
    '''Parses the query string of the incoming request and splits the arguments
    into filters, groupers, and aggregators. It also converts arguments into
    django-compatible formats if necessary'''

    filters = {}
    groupers = {}
    aggregators = {}

    if request.GET:
        for k, v in request.GET.iteritems():
            if k == 'average_by':
                aggregators[k] = v
            elif k == 'group_by':
                groupers[k] = v
            elif k.startswith('timestamp'):
                filters[k] = dateutil.parser.parse(v)
            else:
                filters[k] = v

    return filters, groupers, aggregators


def scalar_data(request):

    # TODO: fix URIs returned in response. Currently they're just the index,
    # but they should be the full URI

    response = {}

    filters, groupers, aggregators = parse_query(request)

    objs = ScalarData.objects.all()
    if filters:
        objs = objs.filter(**filters)

    response['meta'] = {'total_count': objs.count()}

    if groupers:
        # currently assume we're grouping by the sensor_uri
        groups = {}
        for obj in objs:
            obj_dict = {
                'resource_uri': obj.id,
                'value': obj.value,
                'timestamp': obj.timestamp.isoformat(),
            }
            if obj.sensor_id in groups:
                groups[obj.sensor_id].append(obj_dict)
            else:
                groups[obj.sensor_id] = [obj_dict]
        response['sensor_uri_groups'] = groups

    elif aggregators:
        # currently just assume we're averaging by value
        avg_value = objs.aggregate(Avg('value'))['value__avg']
        response['average_value'] = avg_value

    else:
        # no aggregators or groups, so just put all the objects in the response
        response_objects = []
        for obj in objs:
            obj_dict = {
                'resource_uri': obj.id,
                'sensor_uri': obj.sensor_id,
                'value': obj.value,
                'timestamp': obj.timestamp.isoformat(),
            }
            response_objects.append(obj_dict)
        response['objects'] = response_objects

    return HttpResponse(json.dumps(response))


def aggregate_scalar_data(request):
    response_meta = {}
    response_objects = []
    response = {'meta': response_meta, 'objects': response_objects}
    return HttpResponse(json.dumps(response))


# this gets pulled into the main application urlpatterns
urls = patterns(
    '',
    url(r'^$', api_home),
    url(r'^scalar_data/', scalar_data),
    url(r'^aggregate_scalar_data/', aggregate_scalar_data),
)
