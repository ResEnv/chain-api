from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from doppel2.core import api

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf
api_router = routers.DefaultRouter()
api_router.register(r'sites', api.SiteViewSet)
api_router.register(r'devices', api.DeviceViewSet)
api_router.register(r'people', api.PersonViewSet)
api_router.register(r'sensors', api.SensorViewSet)

urlpatterns = patterns(
    '',
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api/', include(api_router.urls)),
    # Examples:
    # url(r'^$', 'doppel2.views.home', name='home'),
    # url(r'^doppel2/', include('doppel2.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
