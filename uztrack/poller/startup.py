from django.conf import settings
from django.utils import timezone

from core.uzgovua.api import SmartApi
from track import queries
from track.models import TrackedWay
from .tasks import poll_history, logger


def run():
    """
    Launches polling tasks for each :class:`track.models.TrackedWayDayHistory`
    history within ``settings.POLLER_WARMUP`` time period.
    """
    api = SmartApi()
    tracked_ways = TrackedWay.objects.all()
    start = timezone.now()
    stop = start + settings.POLLER_WARMUP
    for tracked_way in tracked_ways:
        for history in queries.get_closest_histories(tracked_way):
            starter_eta = poller.calc_random_eta(start, stop)
            logger.info(u'planned start to poll %s on %s' % (history.id, starter_eta))
            poll_history.apply_async(args=(history, api), eta=starter_eta)

    logger.info(u'Polling service started')
