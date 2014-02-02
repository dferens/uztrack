from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'way/create/$', views.WayCreateView.as_view(), name='way_create'),
    url(r'way/(?P<pk>\d+)/$', views.WayDetailView.as_view(), name='way_detail'),
    url(r'way/list/$', views.WayListView.as_view(), name='way_list'),

    url(r'track/create/$', views.TrackedWayCreateView.as_view(), name='track_create'),
    url(r'track/(?P<pk>\d+)/$', views.TrackedWayDetailView.as_view(), name='track_detail'),
    url(r'track/(?P<pk>\d+)/edit/$', views.TrackedWayEditView.as_view(), name='track_edit'),
    url(r'track/list/$', views.TrackedWayListView.as_view(), name='track_list'),
)