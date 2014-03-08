from datetime import datetime, timedelta
from mock import patch

from django.test.utils import override_settings
from django.utils import timezone

from core.tests import TestCase
import track.queries
from track.models import TrackedWayDayHistory as History
from track.tests import TrackedWayFactory, \
                        TrackedWayDayHistoryFactory as HistoryFactory
from .. import queries, tasks


@override_settings(POLLER_AUTOSTART_NEW=False)
class PollTrackedWayTestCase(TestCase):

    def setUp(self):
        self.tracked_way = TrackedWayFactory()
        till_date = datetime.now() + timedelta(days=31)
        for date in self.tracked_way.next_dates(till_date)[:3]:
            HistoryFactory(tracked_way=self.tracked_way,
                           departure_date=date)

    @patch.object(tasks, 'poll_history')
    def test_autostart_disabled(self, mock_poll_history_task):
        queries.poll_tracked_way(self.tracked_way, {})
        self.assertFalse(mock_poll_history_task.apply_async.called)

    @override_settings(POLLER_AUTOSTART_NEW=True)
    @patch.object(track.queries, 'get_closest_histories')
    @patch('poller.queries.poll_history')
    def test_no_or_empty_inspections(self, mock_poll_history_task,
                                           mock_get_closest_histories):
        mock_get_closest_histories.return_value = History.objects.all()

        for scheduled_polls in (None, dict()):
            mock_poll_history_task.reset_mock()
            planned, total = queries.poll_tracked_way(self.tracked_way,
                                                      scheduled_polls)
            self.assertTrue(planned == total == History.objects.count())
            self.assertEqual(mock_poll_history_task.apply_async.call_count,
                             History.objects.count())
            for mock_call in mock_poll_history_task.apply_async.call_args_list:
                call_kwargs = mock_call[1]
                history_id = call_kwargs['args'][0]
                self.assertTrue(History.objects.filter(id=history_id).exists())

    @override_settings(POLLER_AUTOSTART_NEW=True)
    @patch.object(track.queries, 'get_closest_histories')
    @patch('poller.queries.poll_history')
    def test_valid_inspections(self, mock_poll_history_task,
                                     mock_get_closest_histories):
        mock_get_closest_histories.return_value = History.objects.all()
        planned_history = History.objects.all()[0]
        scheduled_polls = { planned_history.id: timezone.now() }

        planned, total = queries.poll_tracked_way(self.tracked_way, scheduled_polls)
        self.assertTrue((planned + 1) == total == History.objects.count())
        mock_calls = mock_poll_history_task.apply_async.call_args_list
        called_history_ids = [c[1]['args'][0] for c in mock_calls]
        self.assertNotIn(planned_history.id, called_history_ids)
