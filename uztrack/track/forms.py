import operator
from functools import partial
from itertools import izip

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from core.uzgovua.api import Api
from core.forms import SubmitFormMixin
from .models import Way, TrackedWay


class WayCreateForm(SubmitFormMixin, forms.ModelForm):
    class Meta:
        model = Way

    def __init__(self, *args, **kwargs):
        super(WayCreateForm, self).__init__(*args, **kwargs)
        self.fields['station_id_from'].widget = forms.HiddenInput()
        self.fields['station_id_to'].widget = forms.HiddenInput()
        for key in self.fields:
            self.fields[key].required = True

    def _clean_station_attr(self, name_attr, id_attr):
        api = Api()
        station_name = self.cleaned_data[name_attr]
        station_id = api.get_station_id(station_name)

        if station_id is None:
            raise forms.ValidationError('Station "%s" does not exist' % station_name)

        del self.errors[id_attr]
        self.cleaned_data[id_attr] = station_id
        return station_name

    def clean_station_from(self):
        return self._clean_station_attr('station_from', 'station_id_from')

    def clean_station_to(self):
        return self._clean_station_attr('station_to', 'station_id_to')


class TrackedWayCreateForm(SubmitFormMixin, forms.ModelForm):
    class Meta:
        model = TrackedWay
        exclude = ('owner',)

    start_time = forms.TimeField(initial='00:00')


class WayDetailForm(WayCreateForm):
    pass


class TrackedWayDetailForm(TrackedWayCreateForm):
    pass
