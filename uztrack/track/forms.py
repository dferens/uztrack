import operator
from functools import partial

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from core import uzgovua
from .models import Way

class WayCreateForm(forms.ModelForm):
    class Meta:
        model = Way

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        super(WayCreateForm, self).__init__(*args, **kwargs)
        self.fields['station_from_id'].widget = forms.HiddenInput()
        self.fields['station_till_id'].widget = forms.HiddenInput()

    def clean(self):
        del self.errors['station_from_id']
        del self.errors['station_till_id']

        cleaned_data = self.cleaned_data
        station_from = cleaned_data['station_from']
        station_till = cleaned_data['station_till']
        station_from_id = uzgovua.get_station_id(station_from)
        station_till_id = uzgovua.get_station_id(station_till)

        if station_from_id is None:
            raise forms.ValidationError('Station "%s" does not exists' % station_from)
        
        if station_till_id is None:
            raise forms.ValidationError('Station "%s" does not exists' % station_till)

        cleaned_data['station_from_id'] = station_from_id
        cleaned_data['station_till_id'] = station_till_id
        return cleaned_data
