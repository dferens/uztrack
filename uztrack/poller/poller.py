import dateutil.parser
from datetime import time
import logging
import random

from django.conf import settings
from django.utils import timezone

from celeryapp import app
from core.utils import total_seconds
from track import queries


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


def calc_next_eta(new_snapshot):
    """
    Calculates eta for next poll basing on previous poll's results.
    """
    if new_snapshot.history.is_critical:
        diff = settings.POLLER_INTERVAL_CRITICAL(new_snapshot.total_places_count)
    else:
        diff = settings.POLLER_INTERVAL

    return new_snapshot.made_on + diff


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
    scheduled = app.control.inspect().scheduled()
    revoked = app.control.inspect().revoked()
    revoked_ids = revoked.values()[0] if revoked else tuple()
    if scheduled is None: return
    else:
        tasks = scheduled.values()[0]
        for task in tasks:
            task_id = task['request']['id']
            history_id = eval(task['request']['args'])[0]
            if (history_id in result) and (task_id not in revoked_ids):
                app.control.revoke(task_id)
            else:
                result[history_id] = dateutil.parser.parse(task['eta'])
        
        return result
