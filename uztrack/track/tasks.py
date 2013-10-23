import datetime
from celery import task

from core.uzgovua.api import Api
from core.uzgovua.raw import Access
from core.utils import DotDict
from .models import (TrackedWay,
                     TrackedWayDayHistory, TrackedWayDayHistorySnapshot)


class Search(object):

    TrackedWaySettings = namedtuple('TrackedWaySettings', 'tracked_way dates')
    TrackedWayDaySettings = namedtuple('TrackedWayDateSettings', 'date history')

    def _get_search_date_limit(self):
        # Ukrainian railways gives us 45 days
        today = datetime.date.today()
        limit = datetime.timedelta(days=45)
        return limit

    def _load_settings(self):
        objects = DotDict()
        search_till = self._get_search_date_limit()
        tracked_ways = TrackedWay.object.all()

        for tracked_way in tracked_ways:
            dates_search_on = tracked_way.next_dates(search_till)
            histories = (TrackedWayDayHistory.objects
                                             .filter(tracked_way=tracked_way,
                                                     departure_date__in=dates_search_on))
            histories = list(histories)
            dates_with_history = histories.values('departure_date')

            for date in dates_search_on:
                if d not in dates_with_history:
                    history = TrackedWayDayHistory(tracked_way=tracked_way,
                                                   departure_date=date)
                    history.save()
                    histories.append(history)

            tracked_way.histories = histories
        objects.tracked_ways = tracked_ways
        return objects

    def _process(self, settings):
        with Access() as api_access:
            for tracked_way_settings in settings.tracked_ways:
                tracked_way = tracked_way_settings.obj
                for history in tracked_way_settings.histories:
                    data = Api.get_stations_routes(tracked_way.way.station_from_id,
                                                   tracked_way.way.station_till_id,
                                                   history.departure_date,
                                                   tracked_way.start_time,
                                                   access=api_access)
                    snapshot = self._make_snapshot(history, data)
                    self._process_snapshot(snapshot)

    def _make_snapshot(self, history, data):
        total_places_count = sum([t.places for t in data.trains])
        snapshot = TrackedWayDayHistorySnapshot(history=history,
                                                total_places_count=total_places_count,
                                                snapshot_data=data)
        snapshot.save()
        return snapshot

    def _process_snapshot(self, snapshot):
        history = snapshot.history
        if history.places_appeared is None:
            if snapshot.total_places_count > 0:
                history.places_appeared = snapshot
                history.save()

        elif history.places_disappeared is None:
            if snapshot.total_places_count == 0:
                history.places_disappeared = snapshot
                history.save()
        else:
            # Regular snapshot
            pass

    def run(self):
        settings = self._load_settings()
        self._process(settings)
