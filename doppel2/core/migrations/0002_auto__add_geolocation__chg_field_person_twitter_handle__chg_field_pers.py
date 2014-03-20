# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GeoLocation'
        db.create_table(u'core_geolocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('elevation', self.gf('django.db.models.fields.FloatField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'core', ['GeoLocation'])


        # Changing field 'Person.twitter_handle'
        db.alter_column(u'core_person', 'twitter_handle', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Person.picture_url'
        db.alter_column(u'core_person', 'picture_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Person.rfid'
        db.alter_column(u'core_person', 'rfid', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))
        # Adding unique constraint on 'Sensor', fields ['device', 'metric']
        db.create_unique(u'core_sensor', ['device_id', 'metric_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Sensor', fields ['device', 'metric']
        db.delete_unique(u'core_sensor', ['device_id', 'metric_id'])

        # Deleting model 'GeoLocation'
        db.delete_table(u'core_geolocation')


        # Changing field 'Person.twitter_handle'
        db.alter_column(u'core_person', 'twitter_handle', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Person.picture_url'
        db.alter_column(u'core_person', 'picture_url', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Person.rfid'
        db.alter_column(u'core_person', 'rfid', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.device': {
            'Meta': {'unique_together': "(['site', 'name', 'building', 'floor', 'room'],)", 'object_name': 'Device'},
            'building': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'floor': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'devices'", 'to': u"orm['core.Site']"})
        },
        u'core.geolocation': {
            'Meta': {'object_name': 'GeoLocation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'elevation': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
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
            'picture_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'rfid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'people'", 'to': u"orm['core.Site']"}),
            'twitter_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.presencedata': {
            'Meta': {'object_name': 'PresenceData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presense_data'", 'to': u"orm['core.Person']"}),
            'present': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presence_data'", 'to': u"orm['core.Sensor']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'core.scalardata': {
            'Meta': {'object_name': 'ScalarData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scalar_data'", 'to': u"orm['core.Sensor']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'core.sensor': {
            'Meta': {'unique_together': "(['device', 'metric'],)", 'object_name': 'Sensor'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sensors'", 'to': u"orm['core.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sensors'", 'to': u"orm['core.Metric']"}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sensors'", 'to': u"orm['core.Unit']"})
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
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status_updates'", 'to': u"orm['core.Person']"}),
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