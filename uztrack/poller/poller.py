import dateutil.parser
from datetime import time
import logging
import random

from django.conf import settings
from django.utils import timezone

from celeryapp import app
from track import queries
from .utils import total_seconds


logger = logging.getLogger('poller.poller')


def poll(history, api):
    """
    Makes api call for a given history and saves results within
    :class:`events.models.TrackedWayDayHistory` snapshot.
    """
    if settings.POLLER_DRY_RUN:
        logger.debug('poller is disabled')
    else:
        stations_routes = api.get_stations_routes(history)    
        return queries.create_snapshot(history, stations_routes)


def calc_next_eta(snapshot, history):
    """
    Calculates eta for next poll basing on previous poll's results.
    """
    return snapshot.made_on + timezone.timedelta(hours=1)


def calc_random_eta(start, stop):
    """
    Returns random datetime within given range.

    :type start: :class:`timezone.datetime`
    :type stop: :class:`timezone.datetime`
    """
    time_range_seconds = total_seconds(stop - start)
    random_eta_seconds = int(random.random() * time_range_seconds)
    return start + timezone.timedelta(seconds=random_eta_seconds)


def calc_stop_eta(history):
    """
    Returns last suitable poll time for a given history.
    
    :type history: :class:`TrackedWayDayHistory`
    :rtype: :class:`timezone.datetime`
    """
    stop_date = history.departure_date + timezone.timedelta(days=1)
    stop_eta_naive = timezone.datetime.combine(stop_date, time(0, 0))
    return timezone.make_aware(stop_eta_naive, timezone.get_current_timezone())


def get_scheduled_polls():
    """
    :rtype: :class:`dict`
    """
    result = dict()
    data = app.control.inspect().scheduled()
    if data is None: return
    else:
        for task in data.values()[0]:
            history_id = eval(task['request']['args'])[0]
            result[history_id] = dateutil.parser.parse(task['eta'])
        return result
