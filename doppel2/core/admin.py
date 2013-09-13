from django.contrib import admin
from doppel2.core.models import SensorGroup, Unit, Metric, Sensor, ScalarData

admin.site.register(SensorGroup)
admin.site.register(ScalarData)
admin.site.register(Sensor)
admin.site.register(Unit)
admin.site.register(Metric)
