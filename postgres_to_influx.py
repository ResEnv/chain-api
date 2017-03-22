from chain.core.models import ScalarData
from django.utils import timezone
from datetime import datetime
from chain.influx_client import InfluxClient, HTTP_STATUS_SUCCESSFUL_WRITE
from chain.core.resources import influx_client

# needs to be run from the manage.py shell context. Entry point is
# `migrate_data`

BATCH_SIZE = 5000
FIRST_TIMESTAMP = datetime.utcfromtimestamp(
    float(1481811788574987776)/1e9).replace(tzinfo=timezone.utc)


def migrate_data(offset, limit=float('inf')):
    '''Returns objects between offset and offset+limit'''
    queryset = ScalarData.objects.filter(
        timestamp__lt=FIRST_TIMESTAMP.isoformat()).order_by('timestamp')
    moved = 0
    while moved < limit:
        n = min(BATCH_SIZE, limit - moved)
        batch_begin = offset+moved
        batch_end = offset+moved+n
        print('Start moving objects[{0}:{1}]...'.format(
            batch_begin,
            batch_end))
        moved_count = post_points(queryset[batch_begin:batch_end])
        print('Moved objects[{0}:{1}]\n'.format(
            batch_begin,
            batch_begin+moved_count))
        moved += moved_count
        if moved_count < n:
            # we moved fewer then we requested, we must be done
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
    print("[{0}] ".format(point.timestamp))
    if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
        raise RuntimeError("Influx returned status {0}".format(
            response.status_code))
    return datacount
