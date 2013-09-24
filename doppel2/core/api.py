from django.http import HttpResponse
from doppel2.core.models import Site, Device
#from django.db.models import Avg
from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse
import json
from datetime import datetime
#import dateutil


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


def site_resource(site):
    if site.url:
        href = site.url
    else:
        href = reverse(sites, args=[site.id])
    return {
        'href': href,
        'name': site.name,
        'latitude': site.latitude,
        'longitude': site.longitude,
        'devices': {'href': reverse(site_devices_collection, args=[site.id])}
    }


def device_resource(device):
    return {
        'href': reverse(devices, args=[device.id]),
        'name': device.name,
        'site': site_resource(device.site),
        'description': device.description,
        'building': device.building,
        'floor': device.floor,
        'room': device.room,
    }


def sites_collection_resource():
    all_sites = Site.objects.all()
    return {
        'href': reverse(sites_collection),
        'meta': {'total_count': all_sites.count()},
        'objects': [site_resource(site) for site in all_sites]
    }


# define the views


def api_home(request):
    # define all the api endpoints
    response = {
        'href': reverse(api_home),
        'sites': sites_collection_resource()
    }
    return HttpResponse(json.dumps(response))


def sites_collection(request):
    response = sites_collection_resource()
    return HttpResponse(json.dumps(response))


def sites(request, site_id):
    site = Site.objects.get(id=site_id)
    response = site_resource(site)
    return HttpResponse(json.dumps(response))


def site_devices_collection(request, site_id):
    devices = Device.objects.filter(site_id=site_id)
    response = {
        'href': reverse(site_devices_collection, args=[site_id]),
        'meta': {'total_count': devices.count()},
        'objects': [device_resource(device) for device in devices]
    }
    return HttpResponse(json.dumps(response))


def sensors(request):
    pass


def devices(request, device_id):
    pass


def scalar_data(request):
    pass
#
#    # TODO: fix URIs returned in response. Currently they're just the index,
#    # but they should be the full URI
#
#    response = {}
#
#    filters, groupers, aggregators = parse_query(request)
#
#    objs = ScalarData.objects.all()
#    if filters:
#        objs = objs.filter(**filters)
#
#    response['meta'] = {'total_count': objs.count()}
#
#    if groupers:
#        # currently assume we're grouping by the sensor_uri
#        groups = {}
#        for obj in objs:
#            obj_dict = {
#                'resource_uri': obj.id,
#                'value': obj.value,
#                'timestamp': obj.timestamp.isoformat(),
#            }
#            if obj.sensor_id in groups:
#                groups[obj.sensor_id].append(obj_dict)
#            else:
#                groups[obj.sensor_id] = [obj_dict]
#        response['sensor_uri_groups'] = groups
#
#    elif aggregators:
#        # currently just assume we're averaging by value
#        avg_value = objs.aggregate(Avg('value'))['value__avg']
#        response['average_value'] = avg_value
#
#    else:
#        # no aggregators or groups, so just put all the objects in the
#        response
#        response_objects = []
#        for obj in objs:
#            obj_dict = {
#                'resource_uri': obj.id,
#                'sensor_uri': obj.sensor_id,
#                'value': obj.value,
#                'timestamp': obj.timestamp.isoformat(),
#            }
#            response_objects.append(obj_dict)
#        response['objects'] = response_objects
#
#    return HttpResponse(json.dumps(response))


# this gets pulled into the main application urlpatterns
urls = patterns(
    '',
    url(r'^$', api_home),
    url(r'^sites/$', sites_collection),
    url(r'^sites/(\d+)$', sites),
    url(r'^sites/(\d+)/devices/', site_devices_collection),
    url(r'^devices/(\d+)$', devices),
)
