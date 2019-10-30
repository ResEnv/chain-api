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

epoch = datetime(1970, 1, 1, 0, 0, 0)
def ms_to_dt(ms):
    return epoch + timedelta(milliseconds=ms)

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

            # select all this sensor's data that doesn't yet have a metric
            query = "SELECT * FROM {0} WHERE sensor_id = '{1}' AND metric = ''".format(measurement,
                                                                       sensor.id)

            print("\rMigrating {} of {} sensors (requesting data)                  ".format(
                sensorsmigrated+1, len(sensors)), end='')
            stdout.flush()
            db_data = influx_client.get_values(influx_client.get(query, True, epoch="ms"))
            print("\r                                                             ", end='')
            stdout.flush()
            print("\rMigrating {} of {} sensors ({} data points)".format(
                sensorsmigrated+1, len(sensors), len(db_data)), end='')
            stdout.flush()
            if agg == "":
                values = [d["value"] for d in db_data]
                print(".", end='')
                stdout.flush()
                try:
                    timestamps = [ms_to_dt(d["time"]) for d in db_data]
                except:
                    print(d["time"])
                    raise
                print(".", end='')
                stdout.flush()
                # TODO: I think under-the-hood this ends up converting back and forth
                # between dict-of-arrays and array-of-dicts format, so there's some
                # opportunity for optimizastion
                influx_client.post_data_bulk(site.id, device.id, sensor.id, sensor.metric, values, timestamps)
                print(".", end='')
                stdout.flush()
            else:
                # import pdb
                # pdb.set_trace()
                query = ""
                for data in db_data:
                    query += "{},sensor_id={},site_id={},device_id={},metric={} min={},max={},count={}i,sum={},mean={} {}".format(
                    measurement, sensor.id, site.id, device.id, sensor.metric,
                    data['min'], data['max'], data['count'], data['sum'], data['mean'],
                    InfluxClient.convert_timestamp(ms_to_dt(data['time']))) + "\n"
                print(".", end='')
                stdout.flush()

                response = influx_client.post('write', query)
                print(".", end='')
                stdout.flush()
                if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
                    raise IntegrityError('Failed Query(status {}):\n{}\nResponse:\n{}'.format(
                        response.status_code, data, response.json()))

            sensorsmigrated += 1
            datamigrated += len(db_data)
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
