# -*- coding: utf-8 -*-
import datetime
import textwrap

import mock
import yaml

from core.tests import TestCase
from track.tests.helpers import TrackedWayDayHistoryFactory as HistoryFactory
from .. import api, data, exceptions
from .test_raw import TokenMock


def get_test_stations_routes(api_obj):
    today, time = datetime.date.today(), datetime.time()
    kwargs = {} if isinstance(api_obj, api.SmartApi) else dict(token=TokenMock())
    return api_obj.get_stations_routes(1, 1, today, time, **kwargs)


class HandleBanTestCase(TestCase):

    def test_ok(self):
        globals = dict(call_count=0)

        @api.handle_ban
        def do(self, *args, **kwargs):
            globals['call_count'] = globals['call_count'] + 1

        do('instance')
        self.assertEqual(globals['call_count'], 1)

    def test_passed(self):
        class MockApi(object):
            call_count = 0
            refreshed = False
            
            def _refresh_token(self):
                MockApi.refreshed = True

            @api.handle_ban
            def do(self, *args, **kwargs):
                MockApi.call_count += 1

                if MockApi.call_count == 1:
                    message = u'Перевищено кількість запитів, 10 хвилин'
                    raise exceptions.BannedApiException(message)
                else:
                    return 'ok'

        MockApi().do()
        self.assertEqual(MockApi.call_count, 2)
        self.assertTrue(MockApi.refreshed)

    def test_didnt_passed(self):
        @api.handle_ban
        def do(self, *args, **kwargs):
            raise exceptions.BannedApiException(
                u'Перевищено кількість запитів, 10 хвилин'
            )

        instance = mock.MagicMock()
        with self.assertRaises(exceptions.BannedApiException):
            do(instance)
        
        self.assertEqual(instance._refresh_token.call_count, 1)


class ApiTestCase(TestCase):

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.api = api.Api()
        self.api._token = TokenMock()

    def test_ok(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            error: false
            data: null
        '''))
        response_data['value'] = {}
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = response_data

            trains = get_test_stations_routes(self.api)
            self.assertIsInstance(trains, data.RouteTrains)

        self.assertEqual(trains.seats_count, 0)

    def test_nothing_found_1(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "По заданому Вами напрямку поїздів немає"
            error: true
            data: null
        '''))
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = response_data

            trains = get_test_stations_routes(self.api)
            self.assertIsInstance(trains, data.RouteTrains)
            self.assertEqual(trains.seats_count, 0)

    def test_nothing_found_2(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "За заданими Вами значенням нічого не знайдено."
            error: true
            data: null
        '''))
        with mock.patch('core.uzgovua.api.requests.post') as mock_post:
            mock_post.return_value.json.return_value = response_data
            trains = get_test_stations_routes(self.api)
            self.assertIsInstance(trains, data.RouteTrains)
            self.assertEqual(trains.seats_count, 0)

    def test_not_available(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "Сервіс тимчасово недоступний"
            error: true
            data: null
        '''))
        with mock.patch('core.uzgovua.api.requests.post') as mock_post:
            mock_post.return_value.json.return_value = response_data
            with self.assertRaises(exceptions.ServiceNotAvailableException):
                get_test_stations_routes(self.api)

    def test_banned(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "Перевищено кількість запитів, 10 хвилин"
            error: true
            data: null
        '''))
        with mock.patch('core.uzgovua.api.requests.post') as mock_post:
            mock_post.return_value.json.return_value = response_data
            with self.assertRaises(exceptions.BannedApiException):
                get_test_stations_routes(self.api)

    def test_unknown_error(self):
        response_data = yaml.safe_load(textwrap.dedent('''
          ---
            value: "???"
            error: true
            data: null
        '''))
        with mock.patch('core.uzgovua.api.requests.post') as mock_post:
            mock_post.return_value.json.return_value = response_data
            with self.assertRaisesRegexp(exceptions.ApiException, r'^\?\?\?$'):
                get_test_stations_routes(self.api)

    def test_get_station_id(self):
        api_object = api.Api()

        # Nothing found
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = dict(value=[])
            self.assertIsNone(api_object.get_station_id('test'))

        # No exact match
        resp = {
            'value': [
                {'title': 'station 1', 'station_id': 1},
                {'title': 'station 2', 'station_id': 2},
            ]
        }
        with mock.patch('core.uzgovua.api.requests.post') as mock_post:
            mock_post.return_value.json.return_value = resp
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
