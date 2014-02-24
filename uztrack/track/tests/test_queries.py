from datetime import date

from model_mommy import mommy

from core.tests import TestCase
from core.uzgovua.data import StationsRoutes
from .helpers import TrackedWayFactory
from .. import models, queries

class QueriesTestCase(TestCase):

    def test_get_closest_histories(self):
        tracked_way = TrackedWayFactory()

        dates = tracked_way.next_dates(queries.get_search_till_date())
        for history in queries.get_closest_histories(tracked_way):
            self.assertIn(history.departure_date, dates)
            self.assertEqual(history.tracked_way, tracked_way)

    def test_create_snapshot(self):
        history = mommy.make(models.TrackedWayDayHistory)
        stations_routes = StationsRoutes()
        stations_routes.seats_count = 0

        snapshot = queries.create_snapshot(history, stations_routes)
        self.assertEqual(snapshot.history, history)
        self.assertEqual(snapshot.total_places_count, 0)

    def test_get_search_till_date(self):
        till_date = queries.get_search_till_date()
        self.assertTrue(isinstance(till_date, date))
