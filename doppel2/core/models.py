from django.db import models
from django.utils import timezone


class Site(models.Model):
    '''An installation of Doppel2, usually on the scale of several or many
    buildings. Sites might be hosted on a remote server, in which case the URL
    field will point to that resource on that server. If the site is hosted
    locally the URL can be blank'''
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    url = models.CharField(max_length=255, default='', blank=True)

    def __repr__(self):
        return 'Site(name=%r, latitude=%r, longitude=%r, url=%r)' % (
            self.name, self.latitude, self.longitude, self.url)

    def __str__(self):
        return self.name


class Person(models.Model):
    '''A Person involved with the site. Some sensors might detect presence of a
    person, so they can reference this model with person-specific
    information'''
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    picture_url = models.CharField(max_length=255, null=True, blank=True)
    twitter_handle = models.CharField(max_length=255, null=True, blank=True)
    rfid = models.CharField(max_length=255, null=True, blank=True)
    site = models.ForeignKey(Site, related_name='people')

    class Meta:
        verbose_name_plural = "people"

    def __repr__(self):
        return ('Person(first_name=%s, last_name=%s, picture_url=%s, ' +
                'twitter_handle=%s, rfid=%s)') % (
                    self.first_name, self.last_name, self.picture_url,
                    self.twitter_handle, self.rfid)

    def __str__(self):
        return " ".join([self.first_name, self.last_name])


class Device(models.Model):
    '''A set of co-located sensors, often sharing a PCB'''
    name = models.CharField(max_length=255)
    site = models.ForeignKey(Site, related_name='devices')
    description = models.TextField(blank=True)
    building = models.CharField(max_length=255, blank=True)
    floor = models.CharField(max_length=10, blank=True)
    room = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ['site', 'name', 'building', 'floor', 'room']

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


class Sensor(models.Model):
    '''An individual sensor. There may be multiple sensors on a single device.
    The metadata field is used to store information that might be necessary to
    tie the Sensor data to the physical Sensor in the real world, such as a MAC
    address, serial number, etc.'''
    device = models.ForeignKey(Device, related_name='sensors')
    metric = models.ForeignKey(Metric, related_name='sensors')
    unit = models.ForeignKey(Unit, related_name='sensors')
    metadata = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ['device', 'metric']

    def __repr__(self):
        return 'Sensor(device=%r, metric=%r, unit=%r)' % (
            self.device, self.metric, self.unit)

    def __str__(self):
        return self.metric.name


class ScalarData(models.Model):
    '''A data point representing scalar sensor data, such as temperature,
    humidity, etc.'''
    sensor = models.ForeignKey(Sensor, related_name='scalar_data')
    timestamp = models.DateTimeField(default=timezone.now, blank=True)
    value = models.FloatField()

    class Meta:
        verbose_name_plural = "scalar data"

    def __repr__(self):
        return 'ScalarData(timestamp=%r, value=%r, sensor=%r)' % (
            self.timestamp, self.value, self.sensor)

    def __str__(self):
        return '%.3f %s' % (self.value, self.sensor.unit)


class PresenceData(models.Model):
    '''Sensor data indicating that a given Person was detected by the sensor at
    the given time, for instance using RFID or face recognition. Note that this
    is also used to indicate that a person was NOT seen by a given sensor by
    setting present=False. Typically a Presence sensor should indicate once
    when a person is first detected, then again when they are first absent.'''

    sensor = models.ForeignKey(Sensor, related_name='presence_data')
    timestamp = models.DateTimeField(default=timezone.now, blank=True)
    person = models.ForeignKey(Person, related_name='presense_data')
    present = models.BooleanField()

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
