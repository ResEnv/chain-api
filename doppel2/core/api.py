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
        'aggragate_scalar_data': reverse(aggregate_scalar_data),
    }
    return HttpResponse(json.dumps(api_endpoints))


def scalar_data(request):
    # plus fields from model
    # allow filtering on timestamp
    #unit = fields.CharField()
    #metric = fields.CharField()
    response_meta = {}
    response_objects = []

    objs = ScalarData.objects.all()
    if request.GET:
        filters = {}
        for k, v in request.GET.iteritems():
            if k.startswith('timestamp'):
                filters[k] = dateutil.parser.parse(v)
            else:
                filters[k] = v

        objs = objs.filter(**filters)

    for obj in objs:
        obj_dict = {
            'value': obj.value,
            'timestamp': obj.timestamp.isoformat(),
            'metric': obj.sensor.metric.name,
            'unit': obj.sensor.unit.name,
        }
        response_objects.append(obj_dict)

    response = {'meta': response_meta, 'objects': response_objects}
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
