import json

from django.core.urlresolvers import reverse
from django.utils import timezone

import mock
from model_mommy import mommy

from core.tests import TestCase
from .helpers import WayFactory, TrackedWayFactory, \
                     TrackedWayDayHistoryFactory, tracked_way_days_generator
from .. models import Way, TrackedWay
from .. import utils, views


class AuthorizedTestCase(TestCase):

    def setUp(self):
        super(AuthorizedTestCase, self).setUp()
        self.auth('testuser', 'password')


class HomeTestCase(TestCase):

    def test_access(self):
        self.assertEqual(self.client.get(self.url('home')).status_code, 200)


class TrackedWayTestCase(AuthorizedTestCase):

    def test_list(self):
        tracked_ways = (TrackedWayFactory(is_repeated=True),
                        TrackedWayFactory(is_repeated=False))
        resp = self.client.get(self.url('trackedway-list'))
        self.assertContains(resp, tracked_ways[0].way)
        self.assertContains(resp, tracked_ways[1].way)
        for weekday in tracked_ways[0].selected_weekdays:
            self.assertContains(resp, weekday)

    def test_create_get(self):
        resp = self.client.get(self.url('trackedway-create'))
        self.assertContains(resp, 'new tracked way')

    def test_create_post_valid(self):
        data = dict(is_regular=True, days=['Monday', 'Tuesday'],
                    station_name_from='test1', station_name_to='test2')
        with mock.patch('track.forms.queries') as mock_queries:
            kwargs = dict(station_id_from=1, station_id_to=2,
                          station_from='test1', station_to='test2')
            mock_queries.get_way.return_value = WayFactory(**kwargs)

            resp = self.client.post(self.url('trackedway-create'), data=data)
            redirect_url = json.loads(resp.content).get('redirect', '')
            self.assertTrue(views.TrackedWayCreateView.success_url == redirect_url)

    def test_create_post_valid_critical(self):
        data = dict(is_regular=False, is_critical=True,
                    departure_date=timezone.now().date(),
                    station_name_from='test1', station_name_to='test2')
        with mock.patch('track.forms.queries') as mock_queries:
            kwargs = dict(station_id_from=1, station_id_to=2,
                          station_from='test1', station_to='test2')
            mock_queries.get_way.return_value = WayFactory(**kwargs)

            resp = self.client.post(self.url('trackedway-create'), data=data)
            self.assertTrue(TrackedWay.objects.last().active_histories[0].is_critical)

    def test_create_post_invalid(self):
        resp = self.client.post(self.url('trackedway-create'), data=dict())
        errors = json.loads(resp.content).get('errors', {})
        self.assertEqual(errors.get('station_name_from', []),
                         ['This field is required.'])
        self.assertEqual(errors.get('station_name_to', []),
                         ['This field is required.'])
        self.assertEqual(errors.get('way', []), ['Way is not specified'])
        self.assertEqual(errors.get('departure_date', []),
                         ['Departure date is not specified'])


    def test_detail(self):
        tracked_way = TrackedWayFactory()
        TrackedWayDayHistoryFactory(tracked_way=tracked_way)
        resp = self.client.get(self.url('trackedway-detail', pk=tracked_way.pk))
        self.assertContains(resp, tracked_way.way.station_from)
        self.assertContains(resp, tracked_way.way.station_to)
        for weekday in tracked_way.selected_weekdays:
            self.assertContains(resp, utils.WEEKDAYS[weekday])
