from django.conf import settings
from django.utils import timezone

from core.uzgovua.api import SmartApi
from track import queries
from track.models import TrackedWay
from .tasks import poll_history
from . import poller


def run():
    """
    Launches polling tasks for each :class:`track.models.TrackedWayDayHistory`
    history within ``settings.POLLER_WARMUP`` time period.
    """
    print '* Launching poller service...'
    api = SmartApi()
    tracked_ways = TrackedWay.objects.all()
    start = timezone.now()
    stop = start + settings.POLLER_WARMUP
    scheduled_polls = poller.get_scheduled_polls()
    planned_polls = total_polls = 0
    for tracked_way in tracked_ways:
        for history in queries.get_closest_histories(tracked_way):
            total_polls += 1
            last_poll_eta = scheduled_polls.get(history.id)
            if last_poll_eta and last_poll_eta > stop:
                print u'- skipping poll for %s' % history.id
                continue
            else:
                starter_eta = poller.calc_random_eta(start, stop)
                stop_on = poller.calc_stop_eta(history)
                print u'- planned start to poll %s on %s' % (history.id, starter_eta)
                poll_history.apply_async(args=(history.id, api, stop_on), eta=starter_eta)
                planned_polls += 1

    print u'* Polling service started (spawned %d/%d) polls\n' % (planned_polls, total_polls)
