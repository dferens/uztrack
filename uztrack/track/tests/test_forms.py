import mock

from core.tests import TestCase
from .. import forms

class WayTestCase(TestCase):

    def test_create(self):
        data = dict(station_id_from=None, station_id_to=None)
        form = forms.WayCreateForm(data)
        self.assertFalse(form.is_valid())

        data.update(station_from='from')
        form = forms.WayCreateForm(data)
        with mock.patch('track.forms.Api') as MockApi:
            MockApi.return_value.get_station_id = lambda id: 1
            self.assertFalse(form.is_valid())

        data.update(station_to='to')
        with mock.patch('track.forms.Api') as MockApi:
            MockApi.return_value.get_station_id = lambda id: None
            form = forms.WayCreateForm(data)
            self.assertFalse(form.is_valid())
            self.assertIn('does not exist', form.errors['station_from'][0])
            self.assertIn('does not exist', form.errors['station_to'][0])

        with mock.patch('track.forms.Api') as MockApi:
            MockApi.return_value.get_station_id = lambda id: 1 if id == 'from' else 2
            form = forms.WayCreateForm(data)
            self.assertTrue(form.is_valid())
