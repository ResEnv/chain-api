from django.apps import apps
from django.test import TestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
# we're just importing this so that the ZMQ monkey-patching happens before any chain stuff
import chain.core.test_core
from chain.localsettings import INFLUX_MEASUREMENT
from chain.core.chaintestcase import ChainTestCase
from django.utils.timezone import now
from datetime import timedelta
from chain.core.resources import influx_client
from chain.influx_client import InfluxClient, HTTP_STATUS_SUCCESSFUL_WRITE
from django.utils.dateparse import parse_datetime


# this came directly from:
# https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/

class TestMigrations(ChainTestCase):
    # for some reason this is returning "chain.core", which throws an error when
    # we actuall use it because the migration graph wants just "core"
    # @property
    # def app(self):
    #     return apps.get_containing_app_config(type(self).__module__).name
    app = 'core'

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        super(TestMigrations, self).setUp()
        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass

class AddInfluxConvenienceTags(TestMigrations):
    # disable writing of influx data by default
    write_scalar_data = False

    migrate_from = '0002_auto_20191017_1403'
    migrate_to = '0003_add_influx_convenience_tags'

    # post data in the old format, so we can test that the upgrade happened
    # successfully
    def old_post_data(self, site_id, device_id, sensor_id, value, timestamp=None):
        timestamp = InfluxClient.convert_timestamp(timestamp)
        data = '{0},sensor_id={1},site_id={2},device_id={3} value={4}'.format(INFLUX_MEASUREMENT,
                                                                              sensor_id,
                                                                              site_id,
                                                                              device_id,
                                                                              value)
        if timestamp:
            data += ' ' + str(timestamp)
        response = influx_client.post('write', data)
        if response.status_code != HTTP_STATUS_SUCCESSFUL_WRITE:
            raise IntegrityError('Error storing data')
        return response

    def setUpBeforeMigration(self, apps):
        # add the data in the old format (without the metric tag)
        for data in self.scalar_data:
            self.old_post_data(data['sensor'].device.site.id,
                               data['sensor'].device.id,
                               data['sensor'].id,
                               data['value'],
                               data['timestamp'])
        influx_client.post('query', '''
                SELECT max("value"), min("value"), mean("value"), count("value"), sum("value")
                INTO "{0}" FROM "{1}" GROUP BY "sensor_id", time(1h), *
            '''.format(INFLUX_MEASUREMENT + '_1h', INFLUX_MEASUREMENT), True)
        influx_client.post('query', '''
                SELECT max("max"), min("min"), sum("sum")/sum("count") as "mean", sum("count") as "count", sum("sum")
                INTO "{0}" FROM "{1}" GROUP BY "sensor_id", time(1d), *
            '''.format(INFLUX_MEASUREMENT + '_1d', INFLUX_MEASUREMENT + '_1h'), True)
        influx_client.post('query', '''
                SELECT max("max"), min("min"), sum("sum")/sum("count") as "mean", sum("count") as "count", sum("sum")
                INTO "{0}" FROM "{1}" GROUP BY "sensor_id", time(1w), *
            '''.format(INFLUX_MEASUREMENT + '_1w', INFLUX_MEASUREMENT + '_1d'), True)

    # now we confirm that the metric tag is present in the migrated data
    def test_tags_migrated(self):
        for sensor in self.sensors:
            queried = sorted(influx_client.get_sensor_data({'sensor_id': sensor.id}),
                             key=lambda d: d["time"])
            expected = sorted(filter(lambda d: d["sensor"].id == sensor.id, self.scalar_data),
                              key=lambda d: d["timestamp"])
            self.assertEqual(len(expected),
                             len(queried))
            for qd, ed in zip(queried, expected):
                self.assertIn("metric", qd.keys())
                self.assertEqual(qd["value"], ed["value"])
                # it seems that somewhere in the round-trip we loose a little accuracy
                self.assertLess(abs(parse_datetime(qd["time"]) - ed["timestamp"]), timedelta(milliseconds=100))
                self.assertEqual(qd["metric"], sensor.metric.name)
            for agg in ["1h", "1d", "1w"]:
                queried = influx_client.get_sensor_data({'sensor_id': sensor.id, 'aggtime': agg})
                for qd in queried:
                    self.assertIn("metric", qd.keys())
                    self.assertEqual(qd["metric"], ed["sensor"].metric.name)
                    values = map(lambda d: d["value"], expected)
                    self.assertEqual(qd["count"], len(values))
                    self.assertEqual(qd["sum"], sum(values))
                    self.assertEqual(qd["mean"], sum(values)/len(values))
                    self.assertEqual(qd["min"], min(values))
                    self.assertEqual(qd["max"], max(values))
