from django.conf.urls import patterns, include, url
from doppel2.core.api import ScalarDataResource
from django.contrib import admin
from tastypie.api import Api

admin.autodiscover()

api = Api(api_name='v1')
api.register(ScalarDataResource())

urlpatterns = patterns(
    '',
    url(r'^api/', include(api.urls)),
    # Examples:
    # url(r'^$', 'doppel2.views.home', name='home'),
    # url(r'^doppel2/', include('doppel2.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
