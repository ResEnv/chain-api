from chain.core.models import ScalarData
from django.utils import timezone
from datetime import timedelta, datetime
from chain.influx_client import InfluxClient, HTTP_STATUS_SUCCESSFUL_WRITE
from chain.core.resources import influx_client
import sys

# needs to be run from the manage.py shell context

# start_time is UTC unix timestamp, delta is in days
def get_points(start_time, delta, amount):
    start_time = datetime.utcfromtimestamp(
        float(start_time)).replace(tzinfo=timezone.utc)
    end_time = start_time + timedelta(days=delta)
    data = ScalarData.objects.filter(
        timestamp__gte=start_time.isoformat(),
        timestamp__lt=end_time.isoformat())
    count = 0
    while count<len(data):
        if len(data) - count >= amount:
            post_points(data[count:count+amount])
            count += amount
        else:
            post_points(data[count:])
            break


def post_points(list_of_points):
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
    if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
        pass
    return response


if __name__ == "__main__":
    if len(sys.argv)==4:
        get_points(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
         print('usage: %s <start_time> <timedelta> <number per batch>' % sys.argv[0])
         sys.exit(1)
