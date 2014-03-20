# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Site'
        db.create_table(u'core_site', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
        ))
        db.send_create_signal(u'core', ['Site'])

        # Adding model 'Person'
        db.create_table(u'core_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('picture_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('twitter_handle', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('rfid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Site'])),
        ))
        db.send_create_signal(u'core', ['Person'])

        # Adding model 'Device'
        db.create_table(u'core_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Site'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('building', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('floor', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('room', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'core', ['Device'])

        # Adding unique constraint on 'Device', fields ['site', 'name', 'building', 'floor', 'room']
        db.create_unique(u'core_device', ['site_id', 'name', 'building', 'floor', 'room'])

        # Adding model 'Unit'
        db.create_table(u'core_unit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
        ))
        db.send_create_signal(u'core', ['Unit'])

        # Adding model 'Metric'
        db.create_table(u'core_metric', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'core', ['Metric'])

        # Adding model 'Sensor'
        db.create_table(u'core_sensor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Device'])),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Metric'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Unit'])),
            ('metadata', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'core', ['Sensor'])

        # Adding model 'ScalarData'
        db.create_table(u'core_scalardata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sensor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Sensor'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'core', ['ScalarData'])

        # Adding model 'PresenceData'
        db.create_table(u'core_presencedata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sensor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Sensor'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Person'])),
            ('present', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['PresenceData'])

        # Adding model 'StatusUpdate'
        db.create_table(u'core_statusupdate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Person'])),
            ('status', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'core', ['StatusUpdate'])


    def backwards(self, orm):
        # Removing unique constraint on 'Device', fields ['site', 'name', 'building', 'floor', 'room']
        db.delete_unique(u'core_device', ['site_id', 'name', 'building', 'floor', 'room'])

        # Deleting model 'Site'
        db.delete_table(u'core_site')

        # Deleting model 'Person'
        db.delete_table(u'core_person')

        # Deleting model 'Device'
        db.delete_table(u'core_device')

        # Deleting model 'Unit'
        db.delete_table(u'core_unit')

        # Deleting model 'Metric'
        db.delete_table(u'core_metric')

        # Deleting model 'Sensor'
        db.delete_table(u'core_sensor')

        # Deleting model 'ScalarData'
        db.delete_table(u'core_scalardata')

        # Deleting model 'PresenceData'
        db.delete_table(u'core_presencedata')

        # Deleting model 'StatusUpdate'
        db.delete_table(u'core_statusupdate')


    models = {
        u'core.device': {
            'Meta': {'unique_together': "(['site', 'name', 'building', 'floor', 'room'],)", 'object_name': 'Device'},
            'building': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'floor': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"})
        },
        u'core.metric': {
            'Meta': {'object_name': 'Metric'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'core.person': {
            'Meta': {'object_name': 'Person'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'picture_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rfid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"}),
            'twitter_handle': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.presencedata': {
            'Meta': {'object_name': 'PresenceData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Person']"}),
            'present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Sensor']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'core.scalardata': {
            'Meta': {'object_name': 'ScalarData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Sensor']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'core.sensor': {
            'Meta': {'object_name': 'Sensor'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Metric']"}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Unit']"})
        },
        u'core.site': {
            'Meta': {'object_name': 'Site'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        u'core.statusupdate': {
            'Meta': {'object_name': 'StatusUpdate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Person']"}),
            'status': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'core.unit': {
            'Meta': {'object_name': 'Unit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['core']