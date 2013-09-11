from django.contrib import admin
from doppel2.core.models import ScalarData, Sensor, Unit, Metric

admin.site.register(ScalarData)
admin.site.register(Sensor)
admin.site.register(Unit)
admin.site.register(Metric)
