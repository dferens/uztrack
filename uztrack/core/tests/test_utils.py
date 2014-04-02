import sys

from django.utils import timezone

from .helpers import TestCase
from .. import utils


class UtilsTestCase(TestCase):

    def test_total_seconds(self):
        td = timezone.timedelta(seconds=1, minutes=1, hours=1)

        self.assertEqual(utils.total_seconds(td), 1 + 60 + 3600)
        if sys.version_info.minor > 6:
            self.assertEqual(utils.total_seconds(td), td.total_seconds())
        
