from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^stats/$', views.TotalStatsView.as_view(), name='total-stats'),
)
