from datetime import timedelta, datetime, date
from mock import patch

from django.utils import timezone
from django.test.utils import override_settings

from core.tests import TestCase
import poller.tasks
from .. import queries, utils
from ..models import TrackedWayDayHistory as History
from .helpers import TrackedWayFactory, \
                     TrackedWayDayHistoryFactory as HistoryFactory, \
                     TrackedWayDayHistorySnapshotFactory as SnapshotFactory


class TrackedWayTestCase(TestCase):

    def test_active_histories(self):
        # Repeated history
        tracked_way = TrackedWayFactory()
        dates = tracked_way.next_dates(queries.get_search_till_date())
        for history in tracked_way.active_histories:
            self.assertIn(history.departure_date, dates)
            self.assertEqual(history.tracked_way, tracked_way)

        # Single-day history
        today = date.today()
        tracked_way = TrackedWayFactory(departure_date=today)
        self.assertTrue(tracked_way.active_histories[0].departure_date == today)

        # expired
        with patch('track.models.timezone') as mock_timezone:
            tracked_way.histories.update(active=False)
            self.assertEqual(tracked_way.active_histories, [])

    def test_is_repeated(self):
        today = date.today()
        repeated_tracked_way = TrackedWayFactory(departure_date=None)
        single_day_tracked_way = TrackedWayFactory(departure_date=today)

        self.assertTrue(repeated_tracked_way.is_repeated)
        self.assertFalse(single_day_tracked_way.is_repeated)

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
        mock_startup_tracked_way.delay.assert_called_once_with(tracked_way.id)


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
