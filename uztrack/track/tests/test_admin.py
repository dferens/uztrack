from django.contrib.auth import get_user_model

from model_mommy import mommy

from core.tests import TestCase
from .helpers import TrackedWayFactory
from .. import models


class AdminTestCase(TestCase):

    def setUp(self):
        args = ('admin', 'admin@example.com', 'admin')
        superuser = get_user_model().objects.create_superuser(*args)
        self.client.login(username='admin', password='admin')

    def test_way_list(self):
        way = mommy.make(models.Way)

        resp = self.client.get(self.url('admin:track_way_changelist'))
        self.assertContains(resp, way.station_from)
        self.assertContains(resp, way.station_to)

    def test_tracked_way_list(self):
        tracked_way = TrackedWayFactory()

        resp = self.client.get(self.url('admin:track_trackedway_changelist'))
        self.assertContains(resp, unicode(tracked_way.way))
        for date in tracked_way.selected_weekdays:
            self.assertContains(resp, date)

    def test_history_list(self):
        history = mommy.make(models.TrackedWayDayHistory,
                             tracked_way=TrackedWayFactory())

        model_name = 'trackedwaydayhistory'
        resp = self.client.get(self.url('admin:track_%s_changelist' % model_name))
        self.assertContains(resp, unicode(history.tracked_way.way))
        for date in history.tracked_way.selected_weekdays:
            self.assertContains(resp, date)
