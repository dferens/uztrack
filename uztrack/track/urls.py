from classsettings.urls import url, Scope

from . import views


with Scope(regex=r'^track/', view=views, name='trackedway') as root:
    url('{}$', 'TrackedWayListView', name='{}-list')
    url('{}create/$', 'TrackedWayCreateView', name='{}-create')

    with Scope(regex=r'{}(?P<pk>\d+)/') as trackedway:
        url('{}$', 'TrackedWayDetailView', name='{}-detail')
        url('{}edit/$', 'TrackedWayEditView', name='{}-edit')

        with Scope(id=r'(?P<date>\d{4}-\d{2}-\d{2})') as history:
            url('{}{id}/$', 'TrackedWayHistoryDetailView', name='{}-history-detail')
            url('{}{id}/subscribe/$', 'HistorySubscriptionDetailView', name='history-subscription-detail')


urlpatterns = list(root.urls)
