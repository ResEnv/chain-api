from django.db import models
from django.utils import timezone


class SensorGroup(models.Model):
    '''A set of co-located sensors, often sharing a PCB'''
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    building = models.CharField(max_length=255, blank=True)
    floor = models.CharField(max_length=10, blank=True)
    room = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ['name', 'building', 'floor', 'room']

    def __repr__(self):
        return ('SensorGroup(name=%r, description=%r, building=%r, ' +
                'floor=%r, room=%r)') % (
                    self.name, self.description, self.building,
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
    '''An individual sensor. There may be multiple sensors on a single
    device.'''
    sensor_group = models.ForeignKey(SensorGroup)
    metric = models.ForeignKey(Metric)
    unit = models.ForeignKey(Unit)

    def __repr__(self):
        return 'Sensor(sensor_group=%r, metric=%r, unit=%r)' % (
            self.sensor_group, self.metric, self.unit)

    def __str__(self):
        return self.metric.name


class ScalarData(models.Model):
    '''A data point representing scalar sensor data, such as temperature,
    humidity, etc.'''
    sensor = models.ForeignKey(Sensor)
    timestamp = models.DateTimeField(default=timezone.now, blank=True)
    value = models.FloatField()

    class Meta:
        verbose_name_plural = "scalar data"

    def __repr__(self):
        return 'ScalarData(timestamp=%r, value=%r, sensor=%r)' % (
            self.timestamp, self.value, self.sensor)

    def __str__(self):
        return '%.3f %s' % (self.value, self.sensor.unit)
