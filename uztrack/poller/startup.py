import logging
import functools

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from core.uzgovua.api import SmartApi
from track.models import TrackedWay
from . import poller, queries


logger = logging.getLogger('poller')


def run():
    """
    Launches polling tasks for each registered tracked way within
    ``settings.POLLER_WARMUP`` time period.
    """
    if settings.POLLER_AUTOSTART:
        logger.info('launching poller service...')
        tracked_ways = TrackedWay.objects.all()
        planned_polls = total_polls = 0

        if settings.POLLER_WAIT_FOR_CELERY is not False:
            import time; time.sleep(settings.POLLER_WAIT_FOR_CELERY)

        scheduled_polls = poller.get_scheduled_polls()    
        if scheduled_polls is None:
            raise ImproperlyConfigured("Could not inspect celery workers.")
        elif not scheduled_polls:
            logger.warning('No scheduled tasks found')

        poll = functools.partial(queries.poll_tracked_way,
                                 celery_scheduled_polls=scheduled_polls)
        for (planned, total) in map(poll, tracked_ways):
            planned_polls += planned; total_polls += total;

        logger.info('poller service started, spawned (%d/%d) poll processes',
                    planned_polls, total_polls)
    else:
        logger.info('poller service autostart is disabled')
