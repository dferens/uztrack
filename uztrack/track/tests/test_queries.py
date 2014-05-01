from datetime import date

import mock
from model_mommy import mommy

from core.tests import TestCase
from core.uzgovua.data import RouteTrains
from .helpers import WayFactory, TrackedWayFactory
from .. import models, queries


class GetWayTestCase(TestCase):

    def test_way_exists(self):
        way = WayFactory(station_from='from', station_to='to')
        self.assertEqual(queries.get_way('from', 'to'), way)

    def test_stations_not_found(self):
        with mock.patch('track.queries.Api') as MockApi:
            # Station from not found
            MockApi.return_value.get_station_id = lambda n: None if n == 'from' else 1
            self.assertIsNone(queries.get_way('from', 'to'))

            # Station to not found
            MockApi.return_value.get_station_id = lambda n: None if n == 'to' else 1
            self.assertIsNone(queries.get_way('from', 'to'))

    def test_creates_new(self):
        with mock.patch('track.queries.Api') as MockApi:
            MockApi.return_value.get_station_id = lambda n: 1 if n == 'from' else 2
            way = queries.get_way('from', 'to')
            self.assertEqual(way.station_id_from, 1)
            self.assertEqual(way.station_id_to, 2)


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
