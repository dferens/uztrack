from datetime import timedelta, datetime
from mock import patch

from django.test.utils import override_settings

from core.tests import TestCase
import poller.tasks
from .. import utils
from ..models import TrackedWayDayHistory as History
from .helpers import TrackedWayFactory, \
                     TrackedWayDayHistoryFactory as HistoryFactory, \
                     TrackedWayDayHistorySnapshotFactory as SnapshotFactory


class TrackedWayTestCase(TestCase):

    def test_unicode(self):
        tracked_way = TrackedWayFactory()

        print_value = unicode(tracked_way)
        self.assertIsInstance(print_value, unicode)
        self.assertTrue(len(print_value) > 0)

    def test_next_dates(self):
        tracked_way = TrackedWayFactory()

        now = datetime.now()
        possible_days = [day for day in tracked_way.days._keys
                         if getattr(tracked_way.days, day)]
        dates = tracked_way.next_dates(now + timedelta(days=31))
        weekdays = utils.WEEKDAYS.keys()
        for date in dates:
            self.assertIn(weekdays[date.weekday()], possible_days)


    @override_settings(POLLER_AUTOSTART_NEW=True)
    @patch.object(poller.tasks, 'startup_tracked_way')
    def test_save(self, mock_startup_tracked_way):
        tracked_way = TrackedWayFactory()
        mock_startup_tracked_way.delay.assert_called_once_with(tracked_way)


class HistoryCheckSnapshotTestCase(TestCase):

    def setUp(self):
        self.history = HistoryFactory()

    def test_no_places_appeared_new(self):

        with patch.object(History, 'on_places_appeared') as mock_signal:
            s = SnapshotFactory(history=self.history, total_places_count=1)
            self.assertEqual(self.history.places_appeared, s)
            mock_signal.send.assert_called_once_with(sender=self.history)

    def test_no_places_appeared_still(self):

        with patch.object(History, 'on_places_appeared') as mock_signal:
            SnapshotFactory(history=self.history, total_places_count=0)
            self.assertEqual(self.history.places_appeared, None)
            self.assertFalse(mock_signal.send.called)

    def test_no_places_disappeared_no_appeared(self):

        with patch.object(History, 'on_places_appeared') as mock_appeared, \
             patch.object(History, 'on_places_disappeared') as mock_disappeared:
            SnapshotFactory(history=self.history, total_places_count=0)
            self.assertEqual(self.history.places_appeared, None)
            self.assertEqual(self.history.places_disappeared, None)
            self.assertFalse(mock_appeared.send.called and
                             mock_disappeared.send.called)

    def test_no_places_disappeared_new(self):
        SnapshotFactory(history=self.history, total_places_count=1)

        with patch.object(History, 'on_places_disappeared') as mock_signal:
            s = SnapshotFactory(history=self.history, total_places_count=0)
            self.assertEqual(self.history.places_disappeared, s)
            mock_signal.send.assert_called_once_with(sender=self.history)            

    def test_no_places_disappeared_still(self):
        SnapshotFactory(history=self.history, total_places_count=2)

        with patch.object(History, 'on_places_disappeared') as mock_signal:
            SnapshotFactory(history=self.history, total_places_count=1)
            self.assertEqual(self.history.places_disappeared, None)
            self.assertFalse(mock_signal.send.called)

    def test_places_disappeared_already(self):
        SnapshotFactory(history=self.history, total_places_count=2)
        s = SnapshotFactory(history=self.history, total_places_count=0)

        with patch.object(History, 'on_places_appeared') as mock_appeared, \
             patch.object(History, 'on_places_disappeared') as mock_disappeared:
            SnapshotFactory(history=self.history, total_places_count=0)
            self.assertEqual(self.history.places_disappeared, s)
            self.assertFalse(mock_appeared.send.called and
                             mock_disappeared.send.called)

    def test_regular_snapshot(self):
        SnapshotFactory(history=self.history, total_places_count=2)

        with patch.object(History, 'on_places_appeared') as mock_appeared, \
             patch.object(History, 'on_places_disappeared') as mock_disappeared:
            SnapshotFactory(history=self.history, total_places_count=1)
            self.assertFalse(mock_appeared.send.called and
                             mock_disappeared.send.called)


class HistoryTestCase(TestCase):

    def test_unicode(self):
        history = HistoryFactory()

        print_value = unicode(history)
        self.assertIsInstance(print_value, unicode)
        self.assertTrue(len(print_value) > 0)
        
    def test_last_snapshot(self):
        history = HistoryFactory()
        snapshots = [SnapshotFactory(history=history, total_places_count=c)
                     for c in (2, 1, 0)]

        self.assertEqual(history.last_snapshot, snapshots[-1])
