from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework.routers import DefaultRouter

import track.views
from track.api import HistoryViewSet, SnapshotViewSet

admin.autodiscover()

router = DefaultRouter()
router.register(r'histories', HistoryViewSet, 'api-histories')
router.register(r'snapshots', SnapshotViewSet, 'api-snapshots')

urlpatterns = patterns('',
    url(r'^$', track.views.Home.as_view(), name='home'),
    url(r'^', include('track.urls')),
    url(r'^', include('poller.urls')),

    url(r'^api/', include(router.urls)),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
)

if settings.PROFILE:
    urlpatterns += (url(r'^profiler/', include('profiler.urls')),)
