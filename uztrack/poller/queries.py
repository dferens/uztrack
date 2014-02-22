from django.conf import settings
from django.utils import timezone

from track import queries
from .tasks import poll_history
from . import poller


logger = poller.logger


def poll_tracked_way(tracked_way, celery_scheduled_polls=None):
    """
    Launches polling tasks for given tracked way.

    :type tracked_way: :class:`track.models.TrackedWay`.
    :param celery_scheduled_polls: dict of "history_id:datetime".
    """
    logger.info(u'* Launching poller service for %d', tracked_way.id)
    start = timezone.now()
    stop = start + settings.POLLER_WARMUP
    planned_polls = total_polls = 0

    for history in queries.get_closest_histories(tracked_way):
        total_polls += 1
        if celery_scheduled_polls:
            last_poll_eta = celery_scheduled_polls.get(history.id)
            if last_poll_eta and last_poll_eta > stop:
                logger.info(u'- skipping poll for %s', history.id)
                continue
        else:
            starter_eta = poller.calc_random_eta(start, stop)
            stop_on = poller.calc_stop_eta(history)
            logger.info(u'- planned start to poll %s on %s', history.id, starter_eta)
            poll_history.apply_async(args=(history.id, stop_on), eta=starter_eta)
            planned_polls += 1

    return planned_polls, total_polls

