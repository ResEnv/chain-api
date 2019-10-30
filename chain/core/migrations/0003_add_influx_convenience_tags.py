# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.db import models, migrations
from chain.core.models import ScalarSensor
from chain.core.resources import influx_client
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from chain.influx_client import InfluxClient, HTTP_STATUS_SUCCESSFUL_WRITE
from django.db import IntegrityError

def add_convenience_tags(apps, schema_editor):
    sensors = ScalarSensor.objects.all()
    print("\n\nMigrating data for {} sensors".format(len(sensors)))
    for agg in ["", "_1h", "_1d", "_1w"]:
        measurement = influx_client._measurement + agg
        print("Migrating data from {} measurement...".format(measurement))

        sensorsmigrated = 0
        datamigrated = 0
        for sensor in sensors:
            device = sensor.device
            site = device.site

            # select all this sensor's data that doesn't yet have a metric
            query = "SELECT * FROM {0} WHERE sensor_id = '{1}' AND metric = ''".format(measurement,
                                                                       sensor.id)

            db_data = influx_client.get_values(influx_client.get(query, True))
            print("\rmigrating {} of {} sensors ({} data points)            ".format(
                sensorsmigrated+1, len(sensors), len(db_data)), end='')
            if agg == "":
                values = [d["value"] for d in db_data]
                timestamps = [parse_datetime(d["time"]) for d in db_data]
                # TODO: I think under-the-hood this ends up converting back and forth
                # between dict-of-arrays and array-of-dicts format, so there's some
                # opportunity for optimizastion
                influx_client.post_data_bulk(site.id, device.id, sensor.id, sensor.metric, values, timestamps)
            else:
                # import pdb
                # pdb.set_trace()
                query = ""
                for data in db_data:
                    query += "{},sensor_id={},site_id={},device_id={},metric={} min={},max={},count={}i,sum={},mean={} {}".format(
                    measurement, sensor.id, site.id, device.id, sensor.metric,
                    data['min'], data['max'], data['count'], data['sum'], data['mean'],
                    InfluxClient.convert_timestamp(parse_datetime(data['time']))) + "\n"

                response = influx_client.post('write', query)
                if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
                    raise IntegrityError('Failed Query(status {}):\n{}\nResponse:\n{}'.format(
                        response.status_code, data, response.json()))

            sensorsmigrated += 1
            datamigrated += len(db_data)
        print("\nMigrated {} data points for measurement {}\n".format(datamigrated, measurement))

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
