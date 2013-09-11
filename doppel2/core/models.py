from django.db import models
from django.utils import timezone


class Sensor(models.Model):
    '''An individual sensor'''
    pass


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


class ScalarData(models.Model):
    '''A data point representing scalar sensor data, such as temperature,
    humidity, etc.'''
    timestamp = models.DateTimeField(default=timezone.now, blank=True)
    value = models.FloatField()
    unit = models.ForeignKey(Unit)
    metric = models.ForeignKey(Metric)

    def __repr__(self):
        return 'ScalarData(timestamp=%r, value=%r, unit=%r, metric=%r)' % (
            self.timestamp, self.value, self.unit, self.metric)

    def __str__(self):
        return '%.3f %s' % (self.value, self.unit)
