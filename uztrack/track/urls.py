from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^way/$', views.WayListView.as_view(), name='way-list'),
    url(r'^way/create/$', views.WayCreateView.as_view(), name='way-create'),
    url(r'^way/(?P<pk>\d+)/$', views.WayDetailView.as_view(), name='way-detail'),

    url(r'^track/$', views.TrackedWayListView.as_view(), name='trackedway-list'),
    url(r'^track/create/$', views.TrackedWayCreateView.as_view(), name='trackedway-create'),
    url(r'^track/(?P<pk>\d+)/$',
        views.TrackedWayDetailView.as_view(),
        name='trackedway-detail'),
    url(r'^track/(?P<pk>\d+)/edit/$',
        views.TrackedWayEditView.as_view(),
        name='trackedway-edit'),
    url(r'^track/(?P<pk>\d+)/(?P<date>\d{4}-\d{2}-\d{2})/$',
        views.TrackedWayHistoryDetailView.as_view(),
        name='trackedway-history-detail')
)
