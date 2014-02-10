from django.views.generic import TemplateView
from django.utils import timezone

from track.models import TrackedWay, \
                         TrackedWayDayHistorySnapshot as Snapshot 
from .utils import get_last_snapshot_elapsed


class TotalStatsView(TemplateView):
    """
    TODO: add some tree widget.

    Should display stats about all tracked ways for all days, collected
    into tree-like structure.
    """
    template_name = 'poller/total_stats.html'

    def calc_history_stats(self, history):
        return {
            'history': history,
            'snapshots_count': history.snapshots.count(),
            'relevance': get_last_snapshot_elapsed(history),
        }

    def get_context_data(self):
        last_snapshot_datetime = Snapshot.objects.last().made_on
        tracked_ways = []
        for tracked_way in TrackedWay.objects.all():
            histories = [self.calc_history_stats(h) for h in tracked_way.histories.all()]
            max_relevance = min(h['relevance'] for h in histories)
            snapshots_count = sum(h['snapshots_count'] for h in histories)
            tracked_ways.append({'tracked_way': tracked_way,
                                 'histories': histories,
                                 'relevance': max_relevance,
                                 'snapshots_count': snapshots_count})
        context = {
            'tracked_ways': tracked_ways,
            'relevance': min(t['relevance'] for t in tracked_ways),
            'snapshots_count': sum(t['snapshots_count'] for t in tracked_ways),
        }
        return context
