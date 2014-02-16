import dateutil.parser
from datetime import time
import logging
import random

from django.utils import timezone

from celeryapp import app
from track import queries


logger = logging.getLogger(__file__)


def poll(history, api):
    stations_routes = api.get_stations_routes(history)    
    return queries.create_snapshot(history, stations_routes)


def calc_next_eta(snapshot, history, execution_time):
    return execution_time + timezone.timedelta(hours=1)


def calc_random_eta(start_datetime, stop_datetime):
    """
    Returns random datetime within given range.
    """
    time_range_seconds = (stop_datetime - start_datetime).total_seconds()
    random_eta_seconds = int(random.random() * time_range_seconds)
    return start_datetime + timezone.timedelta(seconds=random_eta_seconds)


def calc_stop_eta(history):
    """
    Returns last suitable poll time for a given :class:`TrackedWayDayHistory`
    instance.
    """
    stop_date = history.departure_date + timezone.timedelta(days=1)
    stop_eta_naive = timezone.datetime.combine(stop_date, time(0, 0))
    return timezone.make_aware(stop_eta_naive, timezone.get_current_timezone())

def get_scheduled_polls():
    inspect = app.control.inspect()
    result = dict()
    data = inspect.scheduled()
    for task in (data.values()[0] if data else tuple()):
        history_id = int(task['request']['args'].split(',')[0][1:])
        result[history_id] = dateutil.parser.parse(task['eta'])
    return result
