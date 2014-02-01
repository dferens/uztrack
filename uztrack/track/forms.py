import operator
from functools import partial

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from core.uzgovua.api import Api
from core.forms import SubmitForm
from .models import Way, TrackedWay


class WayCreateForm(SubmitForm):
    class Meta:
        model = Way

    def __init__(self, *args, **kwargs):
        super(WayCreateForm, self).__init__(*args, **kwargs)
        self.fields['station_id_from'].widget = forms.HiddenInput()
        self.fields['station_id_to'].widget = forms.HiddenInput()

    def clean(self):
        api = Api()
        del self.errors['station_id_from']
        del self.errors['station_id_to']

        cleaned_data = self.cleaned_data
        station_from = cleaned_data['station_from']
        station_to = cleaned_data['station_to']
        station_id_from = api.get_station_id(station_from)
        station_id_to = api.get_station_id(station_to)

        if station_id_from is None:
            raise forms.ValidationError('Station "%s" does not exists' % station_from)
        
        if station_id_to is None:
            raise forms.ValidationError('Station "%s" does not exists' % station_to)

        cleaned_data['station_id_from'] = station_id_from
        cleaned_data['station_id_to'] = station_id_to
        return cleaned_data


class TrackedWayCreateForm(SubmitForm):
    class Meta:
        model = TrackedWay

    start_time = forms.TimeField(initial='00:00')


class WayDetailForm(WayCreateForm):
    pass


class TrackedWayDetailForm(TrackedWayCreateForm):
    pass
