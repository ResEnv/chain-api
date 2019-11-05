# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.db import models, migrations
from chain.core.models import ScalarSensor
from chain.core.resources import influx_client
from django.utils.timezone import now
from datetime import datetime, timedelta
# from django.utils.dateparse import parse_datetime
from chain.influx_client import InfluxClient, HTTP_STATUS_SUCCESSFUL_WRITE
from django.db import IntegrityError
from sys import stdout

CHUNK_LIMIT = 10000
EPOCH = datetime(1970, 1, 1, 0, 0, 0)

def ms_to_dt(ms):
    return EPOCH + timedelta(milliseconds=ms)

def add_convenience_tags(apps, schema_editor):
    sensors = ScalarSensor.objects.all()
    print("\n\nMigrating data for {} sensors".format(len(sensors)))
    stdout.flush()
    for agg in ["", "_1h", "_1d", "_1w"]:
        measurement = influx_client._measurement + agg
        print("Migrating data from {} measurement...".format(measurement))
        stdout.flush()

        sensorsmigrated = 0
        datamigrated = 0
        for sensor in sensors:
            device = sensor.device
            site = device.site

            print("\rMigrating {} of {} sensors (requesting count)                  ".format(
                sensorsmigrated+1, len(sensors)), end='')
            stdout.flush()
            # doesn't really matter which column we use for the aggregates
            countcol = "value" if agg == "" else "mean"
            countdata = influx_client.get(
                "SELECT COUNT({}) FROM {} WHERE sensor_id = '{}' AND metric = ''".format(
                    countcol, measurement, sensor.id), True).json()
            try:
                assert len(countdata["results"]) == 1
                result = countdata["results"][0]
                if result == {}:
                    sensorsmigrated += 1
                    continue
                assert len(result["series"]) == 1
                series = result["series"][0]
                assert len(series["columns"]) == 2
                assert len(series["values"]) == 1
                count = series["values"][0][series["columns"].index("count")]
            except:
                print("\n==============================")
                print(countdata)
                print("================================")
                raise
            # select all this sensor's data that doesn't yet have a metric
            # apparently working through large datasets with LIMIT and OFFSET
            # is slow, so we'll go through time instead
            starttime = 0
            offset = 0
            while True:
                # note this doesn't work if you specify the time as {}ns explicitly
                query = "SELECT * FROM {} WHERE time > {} AND sensor_id = '{}' AND metric = '' LIMIT {}".format( measurement, starttime, sensor.id, CHUNK_LIMIT)

                print("\rMigrating {} of {} sensors (requesting data {} of {})                  ".format(
                    sensorsmigrated+1, len(sensors), offset+1, count), end='')
                stdout.flush()
                db_data = influx_client.get_values(influx_client.get(query, True, epoch="ns"))
                if len(db_data) == 0:
                    break
                print("\rMigrating {} of {} sensors (processing values for {} of {})             ".format(
                    sensorsmigrated+1, len(sensors), offset+1, count), end='')
                stdout.flush()
                if agg == "":
                    values = [d["value"] for d in db_data]
                    print("\rMigrating {} of {} sensors (processing timestamps for {} of {})             ".format(
                        sensorsmigrated+1, len(sensors), offset+1, count), end='')
                    stdout.flush()
                    try:
                        timestamps = [ms_to_dt(d["time"]/1000000) for d in db_data]
                    except:
                        print(d["time"])
                        raise
                    # TODO: I think under-the-hood this ends up converting back and forth
                    # between dict-of-arrays and array-of-dicts format, so there's some
                    # opportunity for optimizastion
                    print("\rMigrating {} of {} sensors (posting data {} of {})                ".format(
                        sensorsmigrated+1, len(sensors), offset+1, count), end='')
                    stdout.flush()
                    influx_client.post_data_bulk(site.id, device.id, sensor.id, sensor.metric, values, timestamps)
                else:
                    querylines = []
                    print("\rMigrating {} of {} sensors (building query for data {} of {})                ".format(
                        sensorsmigrated+1, len(sensors), offset+1, count), end='')
                    stdout.flush()
                    for data in db_data:
                        fieldstrs = []
                        for rollup in ['min', 'max', 'sum', 'mean']:
                            if data[rollup] is not None:
                                fieldstrs.append('{}={}'.format(rollup, data[rollup]))
                        if data['count'] is not None:
                            fieldstrs.append('count={}i'.format(data['count']))
                        querylines.append("{},sensor_id={},site_id={},device_id={},metric={} {} {}".format(
                            measurement, sensor.id, site.id, device.id, sensor.metric, ",".join(fieldstrs),
                            InfluxClient.convert_timestamp(ms_to_dt(data['time']/1000000))))

                    print("\rMigrating {} of {} sensors (consolidating query for data {} of {})                ".format(
                        sensorsmigrated+1, len(sensors), offset+1, count), end='')
                    stdout.flush()
                    query = '\n'.join(querylines)
                    print("\rMigrating {} of {} sensors (posting data {} of {})                ".format(
                        sensorsmigrated+1, len(sensors), offset+1, count), end='')
                    stdout.flush()
                    response = influx_client.post('write', query)
                    if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
                        raise IntegrityError('Failed Query(status {}):\n{}\nResponse:\n{}'.format(
                            response.status_code, data, response.json()))
                starttime = db_data[-1]["time"]

                offset += len(db_data)
                datamigrated += len(db_data)

            # we've finished all the data for this sensor, delete the old data
            query = "DELETE FROM {} WHERE sensor_id = '{}' AND metric = ''".format(
                measurement, sensor.id)

            print("\rMigrating {} of {} sensors (deleting old data)                  ".format(
                sensorsmigrated+1, len(sensors)), end='')
            stdout.flush()
            influx_client.post("query", query, True)

            sensorsmigrated += 1
        print("\nMigrated {} data points for measurement {}\n".format(datamigrated, measurement))
        stdout.flush()

# we don't actually need to remove the tags, they don't do any harm
def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20191017_1403'),
    ]

    operations = [
        migrations.RunPython(add_convenience_tags, noop)
    ]
