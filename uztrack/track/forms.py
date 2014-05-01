import operator
from functools import partial
from itertools import izip

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from core.uzgovua.api import Api
from core.forms import SubmitFormMixin
from . import models, queries


class TrackedWayCreateForm(forms.ModelForm):
    class Meta:
        model = models.TrackedWay
        exclude = ('owner',)
        widgets = {
            'way': forms.HiddenInput()
        }

    is_repeated = forms.BooleanField(required=False)
    station_name_from = forms.CharField(min_length=2)
    station_name_to = forms.CharField(min_length=2)

    def __init__(self, *args, **kwargs):
        super(TrackedWayCreateForm, self).__init__(*args, **kwargs)
        self.fields['way'].required = False

    def clean(self):
        cleaned_data = super(TrackedWayCreateForm, self).clean()

        if cleaned_data['is_repeated']:
            if cleaned_data['days'] == 0:
                self._errors['days'] = self.error_class(['At least one day should be specified'])
        else:
            if not cleaned_data['departure_date']:
                self._errors['departure_date'] = self.error_class(['Departure date not specified'])

        if 'station_name_from' in cleaned_data and \
           'station_name_to' in cleaned_data:
            cleaned_data['way'] = queries.get_way(cleaned_data['station_name_from'],
                                                  cleaned_data['station_name_to'])
            if cleaned_data['way'] is None:
                raise forms.ValidationError('No such way')

        return cleaned_data


class TrackedWayDetailForm(TrackedWayCreateForm):
    pass


class HistorySubscriptionForm(SubmitFormMixin, forms.ModelForm):
    class Meta:
        model = models.HistorySubscription
        exclude = ('history',)
