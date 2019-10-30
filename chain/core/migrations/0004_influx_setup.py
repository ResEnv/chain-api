# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from chain.core.resources import influx_client
from chain.localsettings import INFLUX_DATABASE, INFLUX_MEASUREMENT

def add_cqs(apps, schema_editor):
    influx_client.post('query', '''
     CREATE CONTINUOUS QUERY "cq_1h" ON "{0}"
         RESAMPLE EVERY 1h
         BEGIN
             SELECT max("value"), min("value"), mean("value"), count("value"), sum("value")
             INTO "{1}" FROM "{2}" GROUP BY "sensor_id", time(1h), *
         END
     '''.format(INFLUX_DATABASE, INFLUX_MEASUREMENT + '_1h', INFLUX_MEASUREMENT), True)
    influx_client.post('query', '''
        CREATE CONTINUOUS QUERY "cq_1d" ON "{0}"
            RESAMPLE FOR 2d
            BEGIN
                SELECT max("max"), min("min"), sum("sum")/sum("count") as "mean", sum("count") as "count", sum("sum")
                INTO "{1}" FROM "{2}" GROUP BY "sensor_id", time(1d), *
            END
        '''.format(INFLUX_DATABASE, INFLUX_MEASUREMENT + '_1d', INFLUX_MEASUREMENT + '_1h'), True)
    influx_client.post('query', '''
        CREATE CONTINUOUS QUERY "cq_1w" ON "{0}"
            RESAMPLE FOR 2w
            BEGIN
                SELECT max("max"), min("min"), sum("sum")/sum("count") as "mean", sum("count") as "count", sum("sum")
                INTO "{1}" FROM "{2}" GROUP BY "sensor_id", time(1w), *
            END
        '''.format(INFLUX_DATABASE, INFLUX_MEASUREMENT + '_1w', INFLUX_MEASUREMENT + '_1d'), True)

def remove_cqs(apps, schema_editor):
    influx_client.post('query',
                       'DROP CONTINUOUS QUERY "cq_1h" on "{}"'.format(INFLUX_DATABASE), True)
    influx_client.post('query',
                       'DROP CONTINUOUS QUERY "cq_1d" on "{}"'.format(INFLUX_DATABASE), True)
    influx_client.post('query',
                       'DROP CONTINUOUS QUERY "cq_1w" on "{}"'.format(INFLUX_DATABASE), True)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_influx_convenience_tags'),
    ]

    operations = [
        migrations.RunPython(add_cqs, remove_cqs)
    ]
