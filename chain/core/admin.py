from django.contrib import admin
from chain.core.models import (Site, Device, Unit, Metric, ScalarSensor,
                                 ScalarData, Person, GeoLocation,
                                 PresenceData, PresenceSensor)


admin.site.register(GeoLocation)
admin.site.register(Site)
admin.site.register(Device)
admin.site.register(ScalarData)
admin.site.register(ScalarSensor)
admin.site.register(Unit)
admin.site.register(Metric)
admin.site.register(Person)
admin.site.register(PresenceData)
admin.site.register(PresenceSensor)
