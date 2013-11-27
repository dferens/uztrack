import datetime
import logging
from celery import task
from collections import namedtuple

from django.conf import settings

from core.uzgovua.api import Api, ApiSession
from core.utils import DotDict
from .models import (TrackedWay,
                     TrackedWayDayHistory, TrackedWayDayHistorySnapshot)


logger = logging.getLogger(__name__)


class SearchTask(object):

    TrackedWaySettings = namedtuple('TrackedWaySettings', 'tracked_way dates')
    TrackedWayDaySettings = namedtuple('TrackedWayDateSettings', 'date history')

    def _get_search_date_limit(self):
        today = datetime.date.today()
        offset = datetime.timedelta(days=settings.TICKETS_SEARCH_RANGE_DAYS)
        return today + offset

    def _load_settings(self):
        logger.info('Collecting task data')
        objects = DotDict()
        search_till = self._get_search_date_limit()
        tracked_ways = TrackedWay.objects.all()

        for tracked_way in tracked_ways:
            dates_search_on = tracked_way.next_dates(search_till)
            histories = (TrackedWayDayHistory.objects
                                             .filter(tracked_way=tracked_way,
                                                     departure_date__in=dates_search_on))
            dates_with_history = [x.departure_date for x in histories]

            for date in dates_search_on:
                if date not in dates_with_history:
                    history = TrackedWayDayHistory(tracked_way=tracked_way,
                                                   departure_date=date)
                    history.save()

        objects.tracked_ways = tracked_ways
        logger.info('%s tracked ways, %s days to check',
                    len(objects.tracked_ways),
                    sum([x.histories.count() for x in objects.tracked_ways]))
        return objects

    def _process(self, settings):
        logger.info('Started grabbing data from uzgovua')
        with ApiSession() as api:
            for tracked_way in settings.tracked_ways:
                for history in tracked_way.histories.all():
                    data = api.get_stations_routes(tracked_way.way.station_from_id,
                                                   tracked_way.way.station_till_id,
                                                   history.departure_date,
                                                   tracked_way.start_time)
                    self._make_snapshot(history, data)

    def _make_snapshot(self, history, data):
        total_places_count = sum([t.places.total for t in data.trains])
        snapshot = TrackedWayDayHistorySnapshot(history=history,
                                                total_places_count=total_places_count,
                                                snapshot_data=data)
        snapshot.save()
        logger.info('Made snapshot (route "%s", %d places)',
                     snapshot.history.tracked_way.way,
                     snapshot.total_places_count)
        return snapshot

    def search(self):
        settings = self._load_settings()
        self._process(settings)


@task
def search():
    SearchTask().search()
