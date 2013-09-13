# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SensorGroup'
        db.create_table(u'core_sensorgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('building', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('floor', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('room', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'core', ['SensorGroup'])

        # Adding unique constraint on 'SensorGroup', fields ['name', 'building', 'floor', 'room']
        db.create_unique(u'core_sensorgroup', ['name', 'building', 'floor', 'room'])

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
            ('sensor_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SensorGroup'])),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Metric'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Unit'])),
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


    def backwards(self, orm):
        # Removing unique constraint on 'SensorGroup', fields ['name', 'building', 'floor', 'room']
        db.delete_unique(u'core_sensorgroup', ['name', 'building', 'floor', 'room'])

        # Deleting model 'SensorGroup'
        db.delete_table(u'core_sensorgroup')

        # Deleting model 'Unit'
        db.delete_table(u'core_unit')

        # Deleting model 'Metric'
        db.delete_table(u'core_metric')

        # Deleting model 'Sensor'
        db.delete_table(u'core_sensor')

        # Deleting model 'ScalarData'
        db.delete_table(u'core_scalardata')


    models = {
        u'core.metric': {
            'Meta': {'object_name': 'Metric'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Metric']"}),
            'sensor_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.SensorGroup']"}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Unit']"})
        },
        u'core.sensorgroup': {
            'Meta': {'unique_together': "(['name', 'building', 'floor', 'room'],)", 'object_name': 'SensorGroup'},
            'building': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'floor': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'core.unit': {
            'Meta': {'object_name': 'Unit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['core']