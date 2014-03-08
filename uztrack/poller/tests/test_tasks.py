from mock import patch
from requests.exceptions import ConnectionError

from django.utils import timezone

from core.tests import TestCase
from track.tests import TrackedWayDayHistoryFactory as HistoryFactory, \
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
