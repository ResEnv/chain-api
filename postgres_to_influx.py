from chain.core.models import ScalarData
from django.utils import timezone
from datetime import timedelta, datetime
from chain.influx_client import InfluxClient, HTTP_STATUS_SUCCESSFUL_WRITE
from chain.core.resources import influx_client
import sys

# needs to be run from the manage.py shell context

def get_points(offset, limit):
    '''Returns objects between offset and offset+limit'''
    print('Start moving objects[{0}:{1}]'.format(
        offset,
        offset+limit))
    data = ScalarData.objects.all()[offset:offset+limit]
    status_code = post_points(data)
    if status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
        print('Failed to move objects[{0}:{1}]'.format(
            offset,
            offset+limit))
    else:
        print('Moved objects[{0}:{1}]'.format(
            offset,
            offset+limit))
    return 

def post_points(list_of_points):
    '''Posts a list of data points to postgres and returns status
    code of request'''
    data = ''
    for point in list_of_points:
        print point['timestamp']
        timestamp = InfluxClient.convert_timestamp(point.timestamp)
        data += '{0},sensor_id={1} value={2} {3}\n'.format(
            influx_client._measurement,
            point.sensor_id,
            point.value,
            timestamp)
    response = influx_client.request('POST',
                                    influx_client._url + '/write',
                                    {'db': influx_client._database},
                                    data)
    return response.status_code


if __name__ == "__main__":
    if len(sys.argv)==4:
        get_points(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
         print('usage: %s <start_time> <timedelta> <number per batch>' % sys.argv[0])
         sys.exit(1)
