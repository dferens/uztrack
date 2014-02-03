import random
from datetime import timedelta

from django.utils import timezone

from track import queries


def poll(history, api):
    stations_routes = api.get_stations_routes(history)    
    return queries.create_snapshot(history, stations_routes)


def calc_next_eta(snapshot, history, execution_time):
    return execution_time + timedelta(hours=1)


def calc_random_eta(**range_kwargs):
    time_range = timedelta(**range_kwargs)
    time_range_seconds = time_range.total_seconds()
    random_eta_seconds = int(random.random() * time_range_seconds)
    return timezone.now() + timedelta(seconds=random_eta_seconds)
