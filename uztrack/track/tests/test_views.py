import mock

from django.core.urlresolvers import reverse

from model_mommy import mommy

from core.tests import TestCase
from .helpers import TrackedWayFactory, TrackedWayDayHistoryFactory, \
                     tracked_way_days_generator
from .. models import Way, TrackedWay
from .. import utils


class AuthorizedTestCase(TestCase):

    def setUp(self):
        super(AuthorizedTestCase, self).setUp()
        self.auth('testuser', 'password')

class WayTestCase(AuthorizedTestCase):

    def test_list(self):
        way = mommy.make(Way, station_from='Station from', station_to='Station to')
        resp = self.client.get(self.url('way-list'))
        self.assertContains(resp, way.station_from)
        self.assertContains(resp, way.station_to)

    def test_create_get(self):
        resp = self.client.get(self.url('way-create'))
        self.assertContains(resp, 'new way')

    def test_create_post(self):
        data = dict(station_from='from', station_to='to',
                    station_id_from='', station_id_to='')
        with mock.patch('track.forms.Api') as MockApi:
            def get_station_id(name):
                return 1 if name == 'from' else 2

            MockApi.return_value.get_station_id = get_station_id
            resp = self.client.post(self.url('way-create'), data=data)
            self.assertRedirects(resp, self.url('way-list'))

    def test_detail(self):
        way = mommy.make(Way)
        resp = self.client.get(self.url('way-detail', pk=way.pk))
        self.assertContains(resp, way.station_from)
        self.assertContains(resp, way.station_to)


class TrackedWayTestCase(AuthorizedTestCase):

    def test_list(self):
        tracked_way = TrackedWayFactory()
        resp = self.client.get(self.url('trackedway-list'))
        self.assertContains(resp, tracked_way.way)
        for weekday in tracked_way.selected_weekdays:
            self.assertContains(resp, weekday)

    def test_create_get(self):
        resp = self.client.get(self.url('trackedway-create'))
        self.assertContains(resp, 'new tracked way')

    def test_create_post(self):
        tracked_way = TrackedWayFactory()
        random_days_handler = tracked_way_days_generator(as_integer=False)
        random_days = [name for (name, is_set) in random_days_handler]
        data = dict(submit='Submit', way=unicode(tracked_way.id),
                    arr_min_time=u'00:00', days=random_days)
        resp = self.client.post(self.url('trackedway-create'), data=data)
        self.assertRedirects(resp, self.url('trackedway-list'))

    def test_detail(self):
        tracked_way = TrackedWayFactory()
        TrackedWayDayHistoryFactory(tracked_way=tracked_way)
        resp = self.client.get(self.url('trackedway-detail', pk=tracked_way.pk))
        self.assertContains(resp, tracked_way.way.station_from)
        self.assertContains(resp, tracked_way.way.station_to)
        for weekday in tracked_way.selected_weekdays:
            self.assertContains(resp, utils.WEEKDAYS[weekday])
