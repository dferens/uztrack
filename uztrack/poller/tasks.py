# -*- coding: utf-8 -*-
import logging
import functools

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from celery.utils.log import get_task_logger
from requests.exceptions import ConnectionError

from celeryapp import app
import track
from track.api import SmartApi
from track.models import TrackedWay, TrackedWayDayHistory as History
from . import poller


api = SmartApi()
logger = get_task_logger(__name__)


@app.task
def poll_history(history_id):
    """
    Polls given :class:`track.models.TrackedWayDayHistory` history with given api
    instance.
    Makes api call, saves results, plans next poll.
    """
    history = History.objects.get(id=history_id)
    execution_time = timezone.now()
    try:
        logger.info('Polling %d history', history_id)
        snapshot = poller.poll(history, api)
    except ConnectionError, e:
        logger.error('Connection error')
        next_poll_eta = execution_time + settings.POLLER_CONNECTION_ERROR_RETRY
        logger.info(u'planned next poll for %s on %s' % (history_id, next_poll_eta))
        poll_history.apply_async(args=(history_id,), eta=next_poll_eta)
    except Exception, e:
        message = e.args[0].encode('utf-8') if e.args else ''
        logger.warning('Exception occured during poll task execution:\n'
                       'History id: %d, date: %s\nException: %s',
                        history_id, history.departure_date, message)
        logger.exception(e)
    else:
        next_poll_eta = poller.calc_next_eta(snapshot, history)
        stop_on = poller.calc_stop_eta(history)
        if next_poll_eta < stop_on:
            next_poll_eta = timezone.localtime(next_poll_eta)
            poll_history.apply_async(args=(history_id,), eta=next_poll_eta)
            logger.info(u'planned next poll for %s on %s' % (history_id, next_poll_eta))
        else:
            history.active = False
            history.save()
            logger.info(u'stopped poll service for %s' % (history_id))


def startup_tracked_way(tracked_way, celery_scheduled_polls=None):
    """
    Launches polling tasks for given tracked way.

    :type tracked_way: :class:`track.models.TrackedWay`.
    :param celery_scheduled_polls: dict of "history_id:datetime".
    """
    if settings.POLLER_AUTOSTART_NEW:
        logger.info('launching poller service for tracked way %d', tracked_way.id)
        start = timezone.localtime(timezone.now())
        stop = start + settings.POLLER_WARMUP
        planned_polls = total_polls = 0

        for history in track.queries.get_closest_histories(tracked_way):
            total_polls += 1
            if celery_scheduled_polls and \
               celery_scheduled_polls.get(history.id) is not None:
                logger.debug('- skipping poll for history %s', history.id)
                continue

            starter_eta = poller.calc_random_eta(start, stop)
            logger.info('- planned start to poll %s on %s', history.id, starter_eta)
            poll_history.apply_async(args=(history.id,), eta=starter_eta)
            planned_polls += 1

        return planned_polls, total_polls
    else:
        logger.info('poller service autostart is disabled by settings')


@app.task
def startup():
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

        poll = functools.partial(startup_tracked_way,
                                 celery_scheduled_polls=scheduled_polls)
        for (planned, total) in map(poll, tracked_ways):
            planned_polls += planned; total_polls += total;

        logger.info('poller service started, spawned (%d/%d) poll processes',
                    planned_polls, total_polls)
    else:
        logger.info('poller service autostart is disabled')
