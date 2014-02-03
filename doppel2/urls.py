from django.conf.urls import patterns, include, url
from django.contrib import admin
from doppel2.core import resources

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^api/', include(resources.urls)),
    # Examples:
    # url(r'^$', 'doppel2.views.home', name='home'),
    # url(r'^doppel2/', include('doppel2.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
