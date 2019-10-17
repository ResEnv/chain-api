# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('building', models.CharField(max_length=255, blank=True)),
                ('floor', models.CharField(max_length=10, blank=True)),
                ('room', models.CharField(max_length=255, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeoLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('elevation', models.FloatField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('key', models.CharField(max_length=255)),
                ('value', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('picture_url', models.CharField(max_length=255, blank=True)),
                ('twitter_handle', models.CharField(max_length=255, blank=True)),
                ('rfid', models.CharField(max_length=255, blank=True)),
                ('geo_location', models.OneToOneField(null=True, blank=True, to='core.GeoLocation')),
            ],
            options={
                'verbose_name_plural': 'people',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PresenceData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('present', models.BooleanField()),
                ('person', models.ForeignKey(related_name='presense_data', to='core.Person')),
            ],
            options={
                'verbose_name_plural': 'presence data',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PresenceSensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('metadata', models.CharField(max_length=255, blank=True)),
                ('device', models.ForeignKey(related_name='presence_sensors', to='core.Device')),
                ('geo_location', models.OneToOneField(null=True, blank=True, to='core.GeoLocation')),
                ('metric', models.ForeignKey(related_name='presence_sensors', to='core.Metric')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScalarSensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('metadata', models.CharField(max_length=255, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('device', models.ForeignKey(related_name='sensors', to='core.Device')),
                ('geo_location', models.OneToOneField(null=True, blank=True, to='core.GeoLocation')),
                ('metric', models.ForeignKey(related_name='sensors', to='core.Metric')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.CharField(default=b'', max_length=255, blank=True)),
                ('raw_zmq_stream', models.CharField(default=b'', max_length=255, blank=True)),
                ('geo_location', models.OneToOneField(null=True, blank=True, to='core.GeoLocation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('status', models.TextField()),
                ('person', models.ForeignKey(related_name='status_updates', to='core.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='scalarsensor',
            name='unit',
            field=models.ForeignKey(related_name='sensors', to='core.Unit'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='scalarsensor',
            unique_together=set([('device', 'metric')]),
        ),
        migrations.AlterUniqueTogether(
            name='presencesensor',
            unique_together=set([('device', 'metric')]),
        ),
        migrations.AddField(
            model_name='presencedata',
            name='sensor',
            field=models.ForeignKey(related_name='presence_data', to='core.PresenceSensor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='site',
            field=models.ForeignKey(related_name='people', to='core.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='geo_location',
            field=models.OneToOneField(null=True, blank=True, to='core.GeoLocation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='site',
            field=models.ForeignKey(related_name='devices', to='core.Site'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='device',
            unique_together=set([('site', 'name', 'building', 'floor', 'room')]),
        ),
    ]
