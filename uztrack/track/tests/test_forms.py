import mock
from datetime import date

from core.tests import TestCase
from .. import forms
from .helpers import WayFactory


class TrackedWayCreateTestCase(TestCase):

    FORM = forms.TrackedWayCreateForm

    def assertIsValid(self, FormClass, form_data):
        form = FormClass(form_data)
        self.assertTrue(form.is_valid())

    def test_clean_ok(self):
        with mock.patch('track.forms.queries') as mock_queries:
            kwargs = dict(station_id_from=1, station_id_to=2,
                          station_from='test1', station_to='test2')
            mock_queries.get_way.return_value = WayFactory(**kwargs)

            self.assertIsValid(self.FORM, {
                'is_repeated': True,
                'days': ['Monday', 'Tuesday'],
                'station_name_from': 'test1',
                'station_name_to': 'test2'
            })
            self.assertIsValid(self.FORM, {
                'is_repeated': False,
                'departure_date': date.today(),
                'station_name_from': 'test1',
                'station_name_to': 'test2'
            })

    def test_clean_no_station_names(self):
        form = self.FORM({
            'is_repeated': True,
            'days': ['Monday']
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        self.assertEqual(form.errors.get('way', ['']),
                         ['Way is not specified'])

    def test_clean_no_days(self):
        form = self.FORM({
            'is_repeated': True,
            'station_name_from': 'test1',
            'station_name_to': 'test2'
        })
        with mock.patch('track.forms.queries') as mock_queries:
            kwargs = dict(station_id_from=1, station_id_to=2,
                          station_from='test1', station_to='test2')
            mock_queries.get_way.return_value = WayFactory(**kwargs)
            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 1)
            self.assertEqual(form.errors.get('days', ['']),
                             ['At least one day should be specified'])

    def test_clean_no_way(self):
        form = self.FORM({
            'is_repeated': True,
            'days': ['Monday'],
            'station_name_from': 'test1',
            'station_name_to': 'test2'
        })
        with mock.patch('track.forms.queries') as mock_queries:
            mock_queries.get_way.return_value = None
            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 1)
            self.assertEqual(form.errors.get('way', ['']), ['No such way'])

    def test_clean_no_departure_date(self):
        form = self.FORM({
            'is_repeated': False,
            'station_name_from': 'test1',
            'station_name_to': 'test2'
        })
        with mock.patch('track.forms.queries') as mock_queries:
            kwargs = dict(station_id_from=1, station_id_to=2,
                          station_from='test1', station_to='test2')
            mock_queries.get_way.return_value = WayFactory(**kwargs)
            self.assertFalse(form.is_valid())
            self.assertEqual(len(form.errors), 1)
            self.assertEqual(form.errors.get('departure_date', ['']),
                             ['Departure date is not specified'])
