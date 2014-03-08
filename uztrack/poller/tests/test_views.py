from core.tests import TestCase
from track.tests.helpers import TrackedWayDayHistoryFactory as HistoryFactory,\
                                TrackedWayDayHistorySnapshotFactory as SnapshotFactory


class ViewsTestCase(TestCase):

    def test_total_stats(self):
        url = self.url('total-stats')
        history = HistoryFactory()
        SnapshotFactory(history=history, _quantity=3)


        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['snapshots_count'], 3)
