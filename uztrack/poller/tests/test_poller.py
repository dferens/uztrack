from mock import MagicMock, patch

from django.utils import timezone
from django.test.utils import override_settings

import celeryapp
from core.tests import TestCase
from core.uzgovua.api import SmartApi
import track.queries
from track.tests import TrackedWayDayHistoryFactory as HistoryFactory, \
                        TrackedWayDayHistorySnapshotFactory as SnapshotFactory
from .. import poller


@override_settings(POLLER_DRY_RUN=False)
class PollerTestCase(TestCase):

    def setUp(self):
        self.history = HistoryFactory()
        SnapshotFactory(history=self.history, total_places_count=5)

    @override_settings(POLLER_DRY_RUN=True)
    def test_poll_dry_run(self):
        mocked_api = MagicMock()
        result = poller.poll(self.history, mocked_api)
        self.assertEqual(result, None)
        self.assertFalse(mocked_api.get_stations_routes.called)

    @patch.object(track.queries, 'create_snapshot')
    def test_poll(self, mocked_create_snapshot):
        mocked_api = MagicMock()
        mocked_create_snapshot.return_value = 'snapshot'

        self.assertEqual(poller.poll(self.history, mocked_api), 'snapshot')
        mocked_api.get_stations_routes.assert_called_once_with(self.history)

    def test_calc_next_eta(self):
        eta = poller.calc_next_eta(self.history.last_snapshot, self.history)
        self.assertIsInstance(eta, timezone.datetime)
        self.assertTrue(timezone.is_aware(eta))

    def test_calc_random_eta(self):
        start, stop = timezone.now(), timezone.now() + timezone.timedelta(seconds=1)
        eta = poller.calc_random_eta(start, stop)
        self.assertIsInstance(eta, timezone.datetime)
        self.assertTrue(start <= eta <= stop)
        self.assertTrue(timezone.is_aware(eta))

    def test_calc_stop_eta(self):
        eta = poller.calc_stop_eta(self.history)
        self.assertIsInstance(eta, timezone.datetime)
        self.assertTrue(eta.date() > self.history.departure_date)
        self.assertTrue(timezone.is_aware(eta))

    @patch.object(celeryapp.app, 'control')
    def test_get_scheduled_polls_no_celery(self, mock_control):
        mock_control.inspect.return_value.scheduled.return_value = None
        self.assertEqual(poller.get_scheduled_polls(), None)

    @patch.object(celeryapp.app, 'control')
    def test_get_scheduled_polls(self, mock_control):
        scheduled_polls_ids = (1, 2)
        sample_inspect_data = eval("""{
            u'celery@HOSTNAME.local': [
                {
                    u'priority': 6,
                    u'eta': u'2014-02-24T22:16:38.468930+02:00',
                    u'request': {
                        u'args': u'(%d,)',
                        u'time_start': None,
                        u'name': u'poller.tasks.poll_history',
                        u'delivery_info': {
                            u'priority': 0,
                            u'redelivered': None,
                            u'routing_key': u'celery',
                            u'exchange':
                            u'celery'
                        },
                        u'hostname': u'celery@HOSTNAME.local',
                        u'acknowledged': False,
                        u'kwargs': u'{}',
                        u'id': u'fdced118-f5c2-4786-abca-00c300664be2',
                        u'worker_pid': None
                    }
                },
                {
                    u'priority': 6,
                    u'eta': u'2014-02-24T22:16:54.434035+02:00',
                    u'request': {
                        u'args': u'(%d,)',
                        u'time_start': None,
                        u'name': u'poller.tasks.poll_history',
                        u'delivery_info': {
                            u'priority': 0,
                            u'redelivered': None,
                            u'routing_key': u'celery',
                            u'exchange': u'celery'
                        },
                        u'hostname': u'celery@HOSTNAME.local',
                        u'acknowledged': False,
                        u'kwargs': u'{}',
                        u'id': u'c8ae6ea5-2242-451b-ad86-527199cd89a2',
                        u'worker_pid': None
                    }
                }
            ]
        }""".strip() % scheduled_polls_ids)
        mock_control.inspect.return_value.scheduled.return_value = sample_inspect_data

        scheduled_polls = poller.get_scheduled_polls()
        self.assertIsInstance(scheduled_polls, dict)
        self.assertEqual(len(scheduled_polls), len(scheduled_polls_ids))
        for scheduled_poll_id in scheduled_polls_ids:
            self.assertIsInstance(scheduled_polls.get(scheduled_poll_id),
                                  timezone.datetime)
