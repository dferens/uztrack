from django.conf.urls import patterns, include
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from track.api import HistoryViewSet


admin.autodiscover()

router = DefaultRouter()
router.register(r'histories', HistoryViewSet)

urlpatterns = patterns('',
    (r'^', include('track.urls')),

    (r'^api/', include(router.urls)),

    (r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),
)
