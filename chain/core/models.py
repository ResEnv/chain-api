from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

class GeoLocation(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.FloatField(null=True, blank=True)


class Metadata(models.Model):
    '''Metadata assoicated with a site, a device, or a sensor'''
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    key = models.CharField(max_length=255)
    value = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now, blank=True)


class Site(models.Model):
    '''An installation of Chain API, usually on the scale of several or many
    buildings. Sites might be hosted on a remote server, in which case the URL
    field will point to that resource on that server. If the site is hosted
    locally the URL can be blank'''
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, default='', blank=True)
    geo_location = models.OneToOneField(GeoLocation, null=True, blank=True)
    raw_zmq_stream = models.CharField(max_length=255, default='', blank=True)

    def __repr__(self):
        return 'Site(name=%r)' % (self.name)

    def __str__(self):
        return self.name


class Device(models.Model):
    '''A set of co-located sensors, often sharing a PCB'''
    name = models.CharField(max_length=255)
    site = models.ForeignKey(Site, related_name='devices')
    description = models.TextField(blank=True)
    building = models.CharField(max_length=255, blank=True)
    floor = models.CharField(max_length=10, blank=True)
    room = models.CharField(max_length=255, blank=True)
    geo_location = models.OneToOneField(GeoLocation, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['site', 'name', 'building', 'floor', 'room']
        ordering = ["name"]

    def __repr__(self):
        return ('Device(site=%r, name=%r, description=%r, building=%r, ' +
                'floor=%r, room=%r)') % (
                    self.site, self.name, self.description, self.building,
                    self.floor, self.room)

    def __str__(self):
        return self.name


class Unit(models.Model):
    '''A unit used on a data point, such as "m", or "kWh"'''
    name = models.CharField(max_length=30, unique=True)

    def __repr__(self):
        return 'Unit(name=%r)' % self.name

    def __str__(self):
        return self.name


class Metric(models.Model):
    '''A metric that might be measured, such as "temperature" or "humidity".
    This is used to tie together a set of ScalarData points that are all
    measuring the same thing.'''
    name = models.CharField(max_length=255, unique=True)

    def __repr__(self):
        return 'Metric(name=%r)' % self.name

    def __str__(self):
        return self.name


class ScalarSensor(models.Model):
    '''An individual sensor. There may be multiple sensors on a single device.
    The metadata field is used to store information that might be necessary to
    tie the Sensor data to the physical Sensor in the real world, such as a MAC
    address, serial number, etc.'''
    device = models.ForeignKey(Device, related_name='sensors')
    metric = models.ForeignKey(Metric, related_name='sensors')
    unit = models.ForeignKey(Unit, related_name='sensors')
    metadata = models.CharField(max_length=255, blank=True)
    geo_location = models.OneToOneField(GeoLocation, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['device', 'metric']

    def __repr__(self):
        return 'Sensor(device=%r, metric=%r, unit=%r)' % (
            self.device, self.metric, self.unit)

    def __str__(self):
        return self.metric.name


class Person(models.Model):
    '''A Person involved with the site. Some sensors might detect presence of a
    person, so they can reference this model with person-specific
    information'''
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    picture_url = models.CharField(max_length=255, blank=True)
    twitter_handle = models.CharField(max_length=255, blank=True)
    rfid = models.CharField(max_length=255, blank=True)
    site = models.ForeignKey(Site, related_name='people')
    geo_location = models.OneToOneField(GeoLocation, null=True, blank=True)

    class Meta:
        verbose_name_plural = "people"

    def __repr__(self):
        return ('Person(first_name=%s, last_name=%s, picture_url=%s, ' +
                'twitter_handle=%s, rfid=%s)') % (
                    self.first_name, self.last_name, self.picture_url,
                    self.twitter_handle, self.rfid)

    def __str__(self):
        return " ".join([self.first_name, self.last_name])


class PresenceSensor(models.Model):
    '''An individual sensor. There may be multiple sensors on a single device.
    The metadata field is used to store information that might be necessary to
    tie the Sensor data to the physical Sensor in the real world, such as a MAC
    address, serial number, etc.'''
    device = models.ForeignKey(Device, related_name='presence_sensors')
    metric = models.ForeignKey(Metric, related_name='presence_sensors')
    # unit = models.ForeignKey(Unit, related_name='sensors')
    metadata = models.CharField(max_length=255, blank=True)
    geo_location = models.OneToOneField(GeoLocation, null=True, blank=True)

    class Meta:
        unique_together = ['device', 'metric']

    def __repr__(self):
        return 'PresenceSensor(device=%r, id=%r)' % (
            self.device, self.id)

    def __str__(self):
        return str(self.metric)
        # self.metric.name


class PresenceData(models.Model):
    '''Sensor data indicating that a given Person was detected by the sensor at
    the given time, for instance using RFID or face recognition. Note that this
    is also used to indicate that a person was NOT seen by a given sensor by
    setting present=False. Typically a Presence sensor should indicate once
    when a person is first detected, then again when they are first absent.'''

    sensor = models.ForeignKey(PresenceSensor, related_name='presence_data')
    timestamp = models.DateTimeField(default=timezone.now, blank=True)
    person = models.ForeignKey(Person, related_name='presense_data')
    present = models.BooleanField(default=None)

    class Meta:
        verbose_name_plural = "presence data"

    def __repr__(self):
        return ('PresenceData(timestamp=%r, sensor=%r, ' +
                'person=%r, present=%r)') % (
                    self.timestamp, self.sensor, self.person, self.present)

    def __str__(self):
        return '%s %spresent' % (self.person,
                                 'not ' if not self.present else '')


class StatusUpdate(models.Model):
    '''Status updates for people, such as tweets, facebook status updates, etc.
    This is probably outside of the scope of a general system for tracking
    sensor data, but is included here for simplicity with the actual
    deployments of DoppelLab. If we deploy this as a generic tool we may want
    to strip this out.'''
    timestamp = models.DateTimeField(default=timezone.now, blank=True)
    person = models.ForeignKey(Person, related_name='status_updates')
    status = models.TextField()
