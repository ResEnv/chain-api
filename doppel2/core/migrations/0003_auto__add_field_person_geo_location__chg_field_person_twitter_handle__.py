# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Person.geo_location'
        db.add_column(u'core_person', 'geo_location',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.GeoLocation'], unique=True, null=True, blank=True),
                      keep_default=False)


        # Changing field 'Person.twitter_handle'
        db.alter_column(u'core_person', 'twitter_handle', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Person.picture_url'
        db.alter_column(u'core_person', 'picture_url', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Person.rfid'
        db.alter_column(u'core_person', 'rfid', self.gf('django.db.models.fields.CharField')(default='', max_length=255))
        # Deleting field 'GeoLocation.object_id'
        db.delete_column(u'core_geolocation', 'object_id')

        # Deleting field 'GeoLocation.content_type'
        db.delete_column(u'core_geolocation', 'content_type_id')

        # Adding field 'Site.geo_location'
        db.add_column(u'core_site', 'geo_location',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.GeoLocation'], unique=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Sensor.geo_location'
        db.add_column(u'core_sensor', 'geo_location',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.GeoLocation'], unique=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Device.geo_location'
        db.add_column(u'core_device', 'geo_location',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.GeoLocation'], unique=True, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Person.geo_location'
        db.delete_column(u'core_person', 'geo_location_id')


        # Changing field 'Person.twitter_handle'
        db.alter_column(u'core_person', 'twitter_handle', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Person.picture_url'
        db.alter_column(u'core_person', 'picture_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Person.rfid'
        db.alter_column(u'core_person', 'rfid', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # User chose to not deal with backwards NULL issues for 'GeoLocation.object_id'
        raise RuntimeError("Cannot reverse this migration. 'GeoLocation.object_id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'GeoLocation.object_id'
        db.add_column(u'core_geolocation', 'object_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'GeoLocation.content_type'
        raise RuntimeError("Cannot reverse this migration. 'GeoLocation.content_type' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'GeoLocation.content_type'
        db.add_column(u'core_geolocation', 'content_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType']),
                      keep_default=False)

        # Deleting field 'Site.geo_location'
        db.delete_column(u'core_site', 'geo_location_id')

        # Deleting field 'Sensor.geo_location'
        db.delete_column(u'core_sensor', 'geo_location_id')

        # Deleting field 'Device.geo_location'
        db.delete_column(u'core_device', 'geo_location_id')


    models = {
        u'core.device': {
            'Meta': {'unique_together': "(['site', 'name', 'building', 'floor', 'room'],)", 'object_name': 'Device'},
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
            'elevation': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {})
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