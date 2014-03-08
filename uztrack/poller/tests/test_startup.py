from mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings
from django.utils import timezone

from core.tests import TestCase
from track.models import TrackedWay
from track.tests import (TrackedWayFactory,
                         TrackedWayDayHistoryFactory as HistoryFactory)
from .. import poller, startup, queries


@override_settings(POLLER_AUTOSTART=True)
class StartupTestCase(TestCase):

    def setUp(self):
        for tracked_way in TrackedWayFactory(_quantity=2):
            HistoryFactory(tracked_way=tracked_way,
                           departure_date=timezone.datetime.today())

    @override_settings(POLLER_AUTOSTART=False)
    @patch.object(queries, 'poll_tracked_way')
    def test_autostart_disabled(self, mock_poll_tracked_way):
        startup.run()
        self.assertFalse(mock_poll_tracked_way.called)

    @patch.object(poller, 'get_scheduled_polls')
    def test_no_inspections(self, mock_get_polls):
        mock_get_polls.return_value = None
        self.assertRaises(ImproperlyConfigured, startup.run)

    @patch.object(poller, 'get_scheduled_polls')
    @patch.object(queries, 'poll_tracked_way')
    def test_inspections_ok(self, mock_poll_tracked_way,
                                                 mock_get_polls):
        mock_get_polls.return_value = {}
        mock_poll_tracked_way.return_value = (1, 2)
        
        startup.run()
        all_tracked_ways = TrackedWay.objects.all()
        self.assertEqual(mock_poll_tracked_way.call_count, len(all_tracked_ways))
        for mock_call in mock_poll_tracked_way.call_args_list:
            tracked_way_arg = mock_call[0][0]
            scheduled_polls_kwarg = mock_call[1]['celery_scheduled_polls']
            self.assertIn(tracked_way_arg, all_tracked_ways)
            self.assertEqual(scheduled_polls_kwarg, {})
