from chain.core.models import ScalarData
from django.utils import timezone
from datetime import timedelta, datetime
from chain.influx_client import InfluxClient, HTTP_STATUS_SUCCESSFUL_WRITE
from chain.core.resources import influx_client
import sys

# needs to be run from the manage.py shell context

BATCH_SIZE = 5000
FIRST_TIMESTAMP = datetime.utcfromtimestamp(
    float(1481811788574987776)/1e9).replace(tzinfo=timezone.utc)

def get_points(offset, limit=None):
    '''Returns objects between offset and offset+limit'''
    if limit == None:
        data = ScalarData.objects.filter(
        timestamp__lt=FIRST_TIMESTAMP.isoformat()).order_by('timestamp')
        print('Start moving objects[{0}:]'.format(offset))
    else:
        print('Start moving objects[{0}:{1}]'.format(
            offset,
            offset+limit))
        data = ScalarData.objects.order_by('timestamp')[offset:offset+limit]

    if len(data)<BATCH_SIZE:
        post_points_wrapper(data)
    else:
        count = 0
        while count < len(data):
            if len(data) - count >= BATCH_SIZE:
                post_points_wrapper(data, count, BATCH_SIZE)
                count += BATCH_SIZEx
            else:
                post_points_wrapper(data, count, len(data)-1)
          
        
    return 

def post_points_wrapper(data, offset, limit):
    print('Moving objects[{0}:{1}]'.format(
        offset,
        offset+limit))
    status_code = post_points(data[offset:offset+limit])
    if status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
        print('Failed to move objects[{0}:{1}]'.format(
            offset,
            offset+limit))
    else:
        print('Moved objects[{0}:{1}]'.format(
            offset,
            offset+limit))
    
def post_points(list_of_points):
    '''Posts a list of data points to postgres and returns status
    code of request'''
    data = ''
    for point in list_of_points:
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
    if len(sys.argv)==3:
        get_points(sys.argv[1],sys.argv[2])
    elif len(sys.argv)==2:
        get_points(sys.argv[1])
    else:
         print('usage: %s <offset> [limit]' % sys.argv[0])
         sys.exit(1)
