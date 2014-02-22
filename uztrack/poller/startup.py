import functools

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from core.uzgovua.api import SmartApi
from track.models import TrackedWay
from . import poller, queries


def run():
    """
    Launches polling tasks for each registered tracked way within
    ``settings.POLLER_WARMUP`` time period.
    """
    print u'* Launching poller service...'
    tracked_ways = TrackedWay.objects.all()
    planned_polls = total_polls = 0
    scheduled_polls = poller.get_scheduled_polls()    
    if scheduled_polls is None:
        raise ImproperlyConfigured("Could not inspect celery workers.")

    poll = functools.partial(queries.poll_tracked_way,
                             celery_scheduled_polls=scheduled_polls)
    for (planned, total) in map(poll, tracked_ways):
        planned_polls += planned; total_polls += total;

    print u'* Polling service started (spawned %d/%d) polls\n' % (planned_polls, total_polls)
