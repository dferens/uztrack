from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
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
        name='trackedway-history-detail'),
    url(r'track/(?P<pk>\d+)/(?P<date>\d{4}-\d{2}-\d{2})/subscribe/$',
        views.HistorySubscriptionDetailView.as_view(),
        name='history-subscription-detail'),
)
