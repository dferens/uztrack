# -*- coding: utf-8 -*-
import datetime
import textwrap

import mock
import yaml

from core.tests import TestCase
from track.tests.helpers import TrackedWayDayHistoryFactory as HistoryFactory
from .. import api, data, exceptions


class ApiTestCase(TestCase):

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.api = api.Api()
        self.api._raw_api = mock.MagicMock()

    def test_nothing_found_1(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "По заданому Вами напрямку поїздів немає"
            error: true
            data: null
        '''))
        self.api._raw_api.get_stations_routes.return_value = response_data
        way_history = HistoryFactory()

        trains = self.api.get_stations_routes(way_history, 'token')
        self.assertIsInstance(trains, data.RouteTrains)
        self.assertEqual(trains.seats_count, 0)

    def test_nothing_found_2(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "За заданими Вами значенням нічого не знайдено."
            error: true
            data: null
        '''))
        self.api._raw_api.get_stations_routes.return_value = response_data
        way_history = HistoryFactory()

        trains = self.api.get_stations_routes(way_history, 'token')
        self.assertIsInstance(trains, data.RouteTrains)
        self.assertEqual(trains.seats_count, 0)

    def test_not_available(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "Сервіс тимчасово недоступний"
            error: true
            data: null
        '''))
        self.api._raw_api.get_stations_routes.return_value = response_data
        way_history = HistoryFactory()

        with self.assertRaises(exceptions.ServiceNotAvailableException):
            self.api.get_stations_routes(way_history, 'token')

    def test_banned(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "Перевищено кількість запитів, 10 хвилин"
            error: true
            data: null
        '''))
        self.api._raw_api.get_stations_routes.return_value = response_data
        way_history = HistoryFactory()

        with self.assertRaises(exceptions.BannedApiException):
            self.api.get_stations_routes(way_history, 'token')

    def test_unknown_error(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "???"
            error: true
            data: null
        '''))
        self.api._raw_api.get_stations_routes.return_value = response_data
        way_history = HistoryFactory()

        with self.assertRaisesRegexp(exceptions.ApiException, r'^\?\?\?$'):
            self.api.get_stations_routes(way_history, 'token')

    def test_get_station_id(self):
        api_object = api.Api()
        api_object._raw_api = mock.MagicMock()

        # Nothing found
        resp = dict(value=[])
        api_object._raw_api.get_station_id.return_value = resp
        self.assertIsNone(api_object.get_station_id('test'))

        # No exact match
        resp = {
            'value': [
                {'title': 'station 1', 'station_id': 1},
                {'title': 'station 2', 'station_id': 2},
            ]
        }
        api_object._raw_api.get_station_id.return_value = resp
        self.assertEqual(api_object.get_station_id('station'), 1)

        # Exact match
        self.assertEqual(api_object.get_station_id('station 2'), 2)


class SmartApiTestCase(TestCase):

    @mock.patch('core.uzgovua.raw.Token')
    def test_token_cache_ok(self, MockToken):
        api_object = api.SmartApi()

        token = api_object.token
        MockToken.assert_called_once_with()
        MockToken.reset_mock()

        token = api_object.token
        self.assertEqual(token.call_count, 0)

    @mock.patch('core.uzgovua.raw.Token')
    def test_token_cache_expires(self, MockToken):
        api_object = api.SmartApi()

        api_object._token_ttl = datetime.timedelta()
        token = api_object.token
        MockToken.assert_called_once_with()
        MockToken.reset_mock()

        token = api_object.token
        MockToken.assert_called_once_with()

    @mock.patch('core.uzgovua.raw.Token')
    @mock.patch.object(api.Api, 'get_stations_routes')
    def test_handle_ban_ok(self, mock_get_stations_routes, MockToken):
        api_object = api.SmartApi()
        api_object._refresh_token = mock.MagicMock()
        api_object._token = 'token'

        api_object.get_stations_routes('asd')
        mock_get_stations_routes.assert_called_once_with('asd', token='token')

    @mock.patch('core.uzgovua.raw.Token')
    def test_handle_ban_passed(self, MockToken):
        api_object = api.SmartApi()
        api_object._raw_api = mock.MagicMock()
        api_object._refresh_token()
        api_object._token = 'expired'

        def mocked_refresh_token(*args, **kwargs):
            api_object._token = 'refreshed'

        def mocked_get_stations_routes(*args, **kwargs):
            token = kwargs.get('token')
            if token == 'expired':
                message = u'Перевищено кількість запитів, 10 хвилин'
                raise exceptions.BannedApiException(message)
            elif token == 'refreshed':
                return dict(error=False)

        api_object._refresh_token = mocked_refresh_token
        api_object._raw_api.get_stations_routes = mocked_get_stations_routes

        history = HistoryFactory()
        result = api_object.get_stations_routes(history)
        self.assertIsNotNone(result)

    @mock.patch('core.uzgovua.raw.Token')
    def test_handle_ban_didnt_passed(self, MockToken):
        api_object = api.SmartApi()
        api_object._raw_api = mock.MagicMock()
        api_object._raw_api.get_stations_routes.side_effect = \
            exceptions.BannedApiException(u'Перевищено кількість запитів, 10 хвилин')

        history = HistoryFactory()
        with self.assertRaises(exceptions.BannedApiException):
            api_object.get_stations_routes(history)
