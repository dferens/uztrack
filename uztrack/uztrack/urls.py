from django.conf.urls import patterns, include
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from track.api import HistoryViewSet, SnapshotViewSet
from poller import startup as poller_startup

admin.autodiscover()

router = DefaultRouter()
router.register(r'histories', HistoryViewSet, 'api-histories')
router.register(r'snapshots', SnapshotViewSet, 'api-snapshots')

urlpatterns = patterns('',
    (r'^', include('track.urls')),

    (r'^api/', include(router.urls)),

    (r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
)
poller_startup.run()
