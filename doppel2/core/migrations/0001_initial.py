# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Unit'
        db.create_table(u'core_unit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'core', ['Unit'])

        # Adding model 'Metric'
        db.create_table(u'core_metric', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'core', ['Metric'])

        # Adding model 'ScalarData'
        db.create_table(u'core_scalardata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Unit'])),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Metric'])),
        ))
        db.send_create_signal(u'core', ['ScalarData'])


    def backwards(self, orm):
        # Deleting model 'Unit'
        db.delete_table(u'core_unit')

        # Deleting model 'Metric'
        db.delete_table(u'core_metric')

        # Deleting model 'ScalarData'
        db.delete_table(u'core_scalardata')


    models = {
        u'core.metric': {
            'Meta': {'object_name': 'Metric'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'core.scalardata': {
            'Meta': {'object_name': 'ScalarData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Metric']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Unit']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'core.unit': {
            'Meta': {'object_name': 'Unit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['core']