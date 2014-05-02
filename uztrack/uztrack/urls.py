from classsettings.urls import url, Scope
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from rest_framework.routers import DefaultRouter

import track.views
from track.api import HistoryViewSet, SnapshotViewSet

admin.autodiscover()

router = DefaultRouter()
router.register(r'histories', HistoryViewSet, 'api-histories')
router.register(r'snapshots', SnapshotViewSet, 'api-snapshots')

with Scope() as root:
    url('^$', track.views.Home, name='home')
    url('^', include('track.urls'))
    url('^', include('poller.urls'))
    url('^api/', include(router.urls))

    url('^admin/', include(admin.site.urls))
    url('^grappelli/', include('grappelli.urls'))

    
    if settings.PROFILE:
        url('^profiler/', include('profiler.urls'))


urlpatterns = list(root.urls)
