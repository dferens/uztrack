from django.conf.urls import patterns, include, url

from .views import WayCreateView, WayListView


urlpatterns = patterns('',
    url(r'way/create/$', WayCreateView.as_view(), name='way_create'),
    url(r'way/list/$', WayListView.as_view(), name='way_list'),
)