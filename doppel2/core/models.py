from django.db import models

# Create your models here.


class Unit(models.Model):
    '''A unit used on a data point, such as "m", or "kWh"'''
    name = models.CharField(max_length=30)


class Metric(models.Model):
    '''A metric that might be measured, such as "temperature" or "humidity".
    This is used to tie together a set of ScalarData points that are all
    measuring the same thing.'''
    name = models.CharField(max_length=30)


class ScalarData(models.Model):
    '''A data point representing scalar sensor data, such as temperature,
    humidity, etc.'''
    timestamp = models.DateTimeField()
    value = models.FloatField()
    unit = models.ForeignKey(Unit)
    metric = models.ForeignKey(Metric)
