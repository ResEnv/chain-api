from __future__ import print_function
from chain.core.models import ScalarData
from django.utils import timezone
from django.db import models
from datetime import datetime
from chain.influx_client import InfluxClient, HTTP_STATUS_SUCCESSFUL_WRITE
from chain.core.resources import influx_client
from sys import stdout

# needs to be run from the manage.py shell context. Entry point is
# `migrate_data`

BATCH_SIZE = 10000
FIRST_TIMESTAMP = datetime.utcfromtimestamp(
    float(1481811788574987776)/1e9).replace(tzinfo=timezone.utc)


def migrate_data(offset, limit=float('inf')):
    '''Returns objects between offset and offset+limit'''
    #queryset = ScalarData.objects.filter(
    #    timestamp__lt=FIRST_TIMESTAMP.isoformat())
    #print('Calculating min and max IDs...')
    #min_max = queryset.aggregate(min=models.Min('id'), max=models.Max('id'))
    #min_id = min_max['min']
    #max_id = min_max['max']
    min_id = 0
    max_id = 1068348868
    print('Got min ID {0} and max ID {0}'.format(min_id, max_id))
    moved = 0
    for i in range(min_id, max_id+1, BATCH_SIZE):
        print('Start moving objects[{0}:{1}]...'.format(
              i, i+BATCH_SIZE), end='')
        stdout.flush()
        moved_count = post_points(ScalarData.objects.filter(id__range=(i, i+BATCH_SIZE-1)))
        print('Moved {0} objects'.format(moved_count))
        stdout.flush()
        moved += moved_count
        if moved >= limit:
            break


def post_points(queryset):
    """Performs the Postgres query and posts the data to influx. Returns the
    number of data points copied"""
    data = ''
    datacount = 0
    for point in queryset:
        timestamp = InfluxClient.convert_timestamp(point.timestamp)
        data += '{0},sensor_id={1} value={2} {3}\n'.format(
            influx_client._measurement,
            point.sensor_id,
            point.value,
            timestamp)
        datacount += 1
    response = influx_client.request('POST',
                                     influx_client._url + '/write',
                                     {'db': influx_client._database},
                                     data)
    # print the timestamp of the last point so we get some sense of where we
    # are
    print("[{0}] ".format(point.timestamp), end='')
    stdout.flush()
    if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
        raise RuntimeError("Influx returned status {0}".format(
            response.status_code))
    return datacount
