from django.conf.urls import patterns, include, url
from django.contrib import admin
from chain.core import resources

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^', include(resources.urls)),
    # Examples:
    # url(r'^$', 'chain.views.home', name='home'),
    # url(r'^chain/', include('chain.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

handler404 = 'chain.core.api.handle404'
