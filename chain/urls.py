from django.conf.urls import patterns, include, url
from django.contrib import admin
from chain.core import resources
from django.conf import settings


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

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

handler404 = 'chain.core.api.handle404'
handler500 = 'chain.core.api.handle500'
