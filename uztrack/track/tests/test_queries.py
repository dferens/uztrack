from datetime import date

from model_mommy import mommy

from core.tests import TestCase
from core.uzgovua.data import RouteTrains
from .helpers import TrackedWayFactory
from .. import models, queries


class QueriesTestCase(TestCase):

    def test_create_snapshot(self):
        history = mommy.make(models.TrackedWayDayHistory)
        stations_routes = RouteTrains()

        snapshot = queries.create_snapshot(history, stations_routes)
        self.assertEqual(snapshot.history, history)
        self.assertEqual(snapshot.total_places_count, 0)

    def test_get_search_till_date(self):
        till_date = queries.get_search_till_date()
        self.assertTrue(isinstance(till_date, date))
