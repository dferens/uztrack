import __builtin__
import mock
import calendar
from datetime import datetime, date, time

from django.utils import timezone

from core.tests import TestCase
from core.uzgovua import data
from .helpers import TrackedWayDayHistoryFactory
from ..api import Api


class ApiTestCase(TestCase):

    def setUp(self):
        self.api = Api()


    def test_get_stations_routes(self):
        history = TrackedWayDayHistoryFactory()
        
        with mock.patch.object(__builtin__, 'super') as mock_super:
            get_routes = mock_super.return_value.get_stations_routes
            get_routes.return_value = data.RouteTrains()

            route_trains = self.api.get_stations_routes(history)
            get_routes.assert_called_once_with(
                history.tracked_way.way.station_id_from,
                history.tracked_way.way.station_id_to,
                history.departure_date, time(0, 0)
            )

    def test_get_stations_routes_with_dep_min_time(self):
        history = TrackedWayDayHistoryFactory()
        history.tracked_way.dep_min_time = time(1, 2)
        
        with mock.patch.object(__builtin__, 'super') as mock_super:
            get_routes = mock_super.return_value.get_stations_routes
            get_routes.return_value = data.RouteTrains()

            route_trains = self.api.get_stations_routes(history)
            get_routes.assert_called_once_with(
                history.tracked_way.way.station_id_from,
                history.tracked_way.way.station_id_to,
                history.departure_date, history.tracked_way.dep_min_time
            )

    def test_get_stations_routes_filters(self):
        history = TrackedWayDayHistoryFactory()
        tracked_way = history.tracked_way

        def time_factory(hours, minutes):
            time_value = time(hours, minutes) 
            dt = datetime.combine(history.departure_date, time_value)
            dt = timezone.make_aware(dt, timezone.get_default_timezone())
            return calendar.timegm(dt.utctimetuple())

        def response_factory(*args, **kwargs):
            """
            Returns next combinations of trains:
            +--------------------------------------+
            |   Num\Hours  0  1  2  3  4  5  6 ... |
            |     (1)      |00000000|              |
            |     (2)         |00000000|           |
            |     (3)            |00000000|        |
            +--------------------------------------+
            """
            return data.RouteTrains({'trains': [
                data.RouteTrain({
                    'station_from': data.StationData({'date': time_factory(0, 0)}),
                    'station_till': data.StationData({'date': time_factory(3, 0)}),
                }),
                data.RouteTrain({
                    'station_from': data.StationData({'date': time_factory(1, 0)}),
                    'station_till': data.StationData({'date': time_factory(4, 0)}),
                }),
                data.RouteTrain({
                    'station_from': data.StationData({'date': time_factory(2, 0)}),
                    'station_till': data.StationData({'date': time_factory(5, 0)}),
                }),
            ]})

        def assertNumberOfTrains(expected):
            self.assertEqual(len(self.api.get_stations_routes(history)), expected)

        with mock.patch.object(__builtin__, 'super') as mock_super:
            mock_super.return_value.get_stations_routes = response_factory
            # No filters
            assertNumberOfTrains(3)
            # Max departure time
            tracked_way.dep_max_time = time(1, 30)
            assertNumberOfTrains(2)
            # Min arrival time
            tracked_way.dep_max_time = None
            tracked_way.arr_min_time = time(3, 30)
            assertNumberOfTrains(2)
            # Max arrival time
            tracked_way.arr_min_time = None
            tracked_way.arr_max_time = time(4, 30)
            assertNumberOfTrains(2)
            # All together
            tracked_way.dep_max_time = time(1, 30)
            tracked_way.arr_max_time = time(3, 30)
            assertNumberOfTrains(1)
            tracked_way.arr_min_time = time(3, 20)
            assertNumberOfTrains(0)
