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
        # TODO: fix tests
        # random_days = [name for (name, is_set) in random_days_handler]
        # data = dict(submit='Submit', way=unicode(tracked_way.id),
        #             arr_min_time=u'00:00', days=random_days)
        # resp = self.client.post(self.url('trackedway-create'), data=data)
        # self.assertRedirects(resp, self.url('trackedway-list'))

    def test_detail(self):
        tracked_way = TrackedWayFactory()
        TrackedWayDayHistoryFactory(tracked_way=tracked_way)
        resp = self.client.get(self.url('trackedway-detail', pk=tracked_way.pk))
        self.assertContains(resp, tracked_way.way.station_from)
        self.assertContains(resp, tracked_way.way.station_to)
        for weekday in tracked_way.selected_weekdays:
            self.assertContains(resp, utils.WEEKDAYS[weekday])
