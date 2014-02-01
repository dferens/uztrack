from django.conf.urls import patterns, include
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
    (r'^', include('track.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
)
