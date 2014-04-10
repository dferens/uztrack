from datetime import datetime, timedelta

from mock import patch
from requests.exceptions import ConnectionError

from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings

from django.utils import timezone

from core.tests import TestCase
import track.queries
from track.models import TrackedWay,TrackedWayDayHistory as History
from track.tests import TrackedWayFactory, \
                        TrackedWayDayHistoryFactory as HistoryFactory, \
                        TrackedWayDayHistorySnapshotFactory as SnapshotFactory
from .. import poller, tasks


class PollHistoryTaskTestCase(TestCase):

    def setUp(self):
        self.history = HistoryFactory(departure_date=timezone.datetime.today())

    @patch.object(tasks.poll_history, 'apply_async')
    @patch.object(poller, 'poll')
    def test_raised_connection_error(self, mock_poll, mocked_apply_async):
        mock_poll.side_effect = ConnectionError

        tasks.poll_history(self.history.id)
        self.assertEqual(mocked_apply_async.call_count, 1)
        task_kwargs = mocked_apply_async.call_args[1]
        self.assertEqual(task_kwargs['args'][0], self.history.id)
        self.assertIsInstance(task_kwargs['eta'], timezone.datetime)

    @patch.object(tasks.poll_history, 'apply_async')
    @patch.object(poller, 'poll')
    def test_raised_other_exception(self, mock_poll, mocked_apply_async):
        mock_poll.side_effect = Exception

        tasks.poll_history(self.history.id)
        self.assertFalse(mocked_apply_async.called)

    @patch.object(tasks.poll_history, 'apply_async')
    @patch.object(poller, 'calc_stop_eta')
    @patch.object(poller, 'poll')
    def test_success_planned_next_poll(self, mock_poll, mock_calc_stop_eta,
                                             mock_apply_async):
        mock_poll.return_value = SnapshotFactory(history=self.history)
        mock_calc_stop_eta.return_value = timezone.make_aware(
            self.history.departure_date + timezone.timedelta(days=1),
            timezone.get_current_timezone()
        )

        tasks.poll_history(self.history.id)
        self.assertTrue(mock_apply_async.called)
        task_kwargs = mock_apply_async.call_args[1]
        self.assertEqual(task_kwargs['args'][0], self.history.id)
        next_eta = task_kwargs['eta']
        self.assertIsInstance(next_eta, timezone.datetime)

    @patch.object(tasks.poll_history, 'apply_async')
    @patch.object(poller, 'calc_stop_eta')
    @patch.object(poller, 'poll')
    def test_success_canceled_next_poll(self, mock_poll, mock_calc_stop_eta,
                                              mock_apply_async):
        mock_poll.return_value = SnapshotFactory(history=self.history)
        mock_calc_stop_eta.return_value = timezone.make_aware(
            self.history.departure_date - timezone.timedelta(days=1),
            timezone.get_current_timezone()
        )

        tasks.poll_history(self.history.id)
        self.assertFalse(mock_apply_async.called)


@override_settings(POLLER_AUTOSTART=True)
class StartupTaskTestCase(TestCase):

    def setUp(self):
        for tracked_way in TrackedWayFactory(_quantity=2):
            HistoryFactory(tracked_way=tracked_way,
                           departure_date=timezone.datetime.today())

    @override_settings(POLLER_AUTOSTART=False)
    @patch.object(tasks, 'startup_tracked_way')
    def test_autostart_disabled(self, mock_startup_tracked_way):
        tasks.startup()
        self.assertFalse(mock_startup_tracked_way.called)

    @patch.object(poller, 'get_scheduled_polls')
    def test_no_inspections(self, mock_get_polls):
        mock_get_polls.return_value = None
        self.assertRaises(ImproperlyConfigured, tasks.startup)

    @patch.object(poller, 'get_scheduled_polls')
    @patch.object(tasks, 'startup_tracked_way')
    def test_inspections_ok(self, mock_startup_tracked_way,
                                                 mock_get_polls):
        mock_get_polls.return_value = {}
        mock_startup_tracked_way.return_value = (1, 2)
        
        tasks.startup()
        all_tracked_ways = TrackedWay.objects.all()
        self.assertEqual(mock_startup_tracked_way.call_count, len(all_tracked_ways))
        for mock_call in mock_startup_tracked_way.call_args_list:
            tracked_way_arg = mock_call[0][0]
            scheduled_polls_kwarg = mock_call[1]['celery_scheduled_polls']
            self.assertIn(tracked_way_arg, all_tracked_ways)
            self.assertEqual(scheduled_polls_kwarg, {})


@override_settings(POLLER_AUTOSTART_NEW=False)
class StartupTrackedWayTestCase(TestCase):

    def setUp(self):
        self.tracked_way = TrackedWayFactory()
        till_date = datetime.now() + timedelta(days=31)
        for date in self.tracked_way.next_dates(till_date)[:3]:
            HistoryFactory(tracked_way=self.tracked_way,
                           departure_date=date)

    @patch.object(tasks, 'poll_history')
    def test_autostart_disabled(self, mock_poll_history_task):
        tasks.startup_tracked_way(self.tracked_way, {})
        self.assertFalse(mock_poll_history_task.apply_async.called)

    @override_settings(POLLER_AUTOSTART_NEW=True)
    @patch.object(track.queries, 'get_closest_histories')
    @patch('poller.tasks.poll_history')
    def test_no_or_empty_inspections(self, mock_poll_history_task,
                                           mock_get_closest_histories):
        mock_get_closest_histories.return_value = History.objects.all()

        for scheduled_polls in (None, dict()):
            mock_poll_history_task.reset_mock()
            planned, total = tasks.startup_tracked_way(self.tracked_way,
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
    @patch('poller.tasks.poll_history')
    def test_valid_inspections(self, mock_poll_history_task,
                                     mock_get_closest_histories):
        mock_get_closest_histories.return_value = History.objects.all()
        planned_history = History.objects.all()[0]
        scheduled_polls = { planned_history.id: timezone.now() }

        planned, total = tasks.startup_tracked_way(self.tracked_way, scheduled_polls)
        self.assertTrue((planned + 1) == total == History.objects.count())
        mock_calls = mock_poll_history_task.apply_async.call_args_list
        called_history_ids = [c[1]['args'][0] for c in mock_calls]
        self.assertNotIn(planned_history.id, called_history_ids)
