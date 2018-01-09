# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Metadata'
        db.create_table(u'core_metadata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
        ))
        db.send_create_signal(u'core', ['Metadata'])


    def backwards(self, orm):
        # Deleting model 'Metadata'
        db.delete_table(u'core_metadata')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.device': {
            'Meta': {'ordering': "['name']", 'unique_together': "(['site', 'name', 'building', 'floor', 'room'],)", 'object_name': 'Device'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'building': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'floor': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'geo_location': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.GeoLocation']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'devices'", 'to': u"orm['core.Site']"})
        },
        u'core.geolocation': {
            'Meta': {'object_name': 'GeoLocation'},
            'elevation': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {})
        },
        u'core.metadata': {
            'Meta': {'object_name': 'Metadata'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'core.metric': {
            'Meta': {'object_name': 'Metric'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'core.person': {
            'Meta': {'object_name': 'Person'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'geo_location': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.GeoLocation']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'picture_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'rfid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'people'", 'to': u"orm['core.Site']"}),
            'twitter_handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'core.presencedata': {
            'Meta': {'object_name': 'PresenceData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presense_data'", 'to': u"orm['core.Person']"}),
            'present': ('django.db.models.fields.BooleanField', [], {}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presence_data'", 'to': u"orm['core.PresenceSensor']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'core.presencesensor': {
            'Meta': {'unique_together': "(['device', 'metric'],)", 'object_name': 'PresenceSensor'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presence_sensors'", 'to': u"orm['core.Device']"}),
            'geo_location': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.GeoLocation']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presence_sensors'", 'to': u"orm['core.Metric']"})
        },
        u'core.scalarsensor': {
            'Meta': {'unique_together': "(['device', 'metric'],)", 'object_name': 'ScalarSensor'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sensors'", 'to': u"orm['core.Device']"}),
            'geo_location': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.GeoLocation']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sensors'", 'to': u"orm['core.Metric']"}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sensors'", 'to': u"orm['core.Unit']"})
        },
        u'core.site': {
            'Meta': {'object_name': 'Site'},
            'geo_location': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.GeoLocation']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'raw_zmq_stream': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
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