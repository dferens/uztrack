import operator
from functools import partial

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from core import uzgovua
from core.forms import SubmitForm
from .models import Way, TrackedWay


class WayCreateForm(SubmitForm):
    class Meta:
        model = Way

    def __init__(self, *args, **kwargs):
        super(WayCreateForm, self).__init__(*args, **kwargs)
        self.fields['station_from_id'].widget = forms.HiddenInput()
        self.fields['station_till_id'].widget = forms.HiddenInput()

    def clean(self):
        del self.errors['station_from_id']
        del self.errors['station_till_id']

        cleaned_data = self.cleaned_data
        station_from = cleaned_data['station_from']
        station_till = cleaned_data['station_till']
        station_from_id = uzgovua.Api.get_station_id(station_from)
        station_till_id = uzgovua.Api.get_station_id(station_till)

        if station_from_id is None:
            raise forms.ValidationError('Station "%s" does not exists' % station_from)
        
        if station_till_id is None:
            raise forms.ValidationError('Station "%s" does not exists' % station_till)

        cleaned_data['station_from_id'] = station_from_id
        cleaned_data['station_till_id'] = station_till_id
        return cleaned_data


class TrackedWayCreateForm(SubmitForm):
    class Meta:
        model = TrackedWay

    start_time = forms.TimeField(initial='00:00')


class WayDetailForm(WayCreateForm):
    pass


class TrackedWayDetailForm(TrackedWayCreateForm):
    pass
