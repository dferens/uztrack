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

    is_regular = forms.BooleanField(required=False)
    station_name_from = forms.CharField(min_length=2)
    station_name_to = forms.CharField(min_length=2)
    way = forms.Field(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(TrackedWayCreateForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder.remove('way')
        self.fields.keyOrder.append('way')

    def clean_way(self):
        if 'station_name_from' in self.cleaned_data and \
           'station_name_to' in self.cleaned_data:
            way = queries.get_way(self.cleaned_data['station_name_from'],
                                  self.cleaned_data['station_name_to'])
            if way is None:
                raise forms.ValidationError('No such way')

            return way

        raise forms.ValidationError('Way is not specified')

    def clean(self):
        cleaned_data = super(TrackedWayCreateForm, self).clean()

        if cleaned_data['is_regular']:
            if cleaned_data['days'] == 0:
                self._errors['days'] = \
                    self.error_class(['At least one day should be specified'])
        else:
            if not cleaned_data['departure_date']:
                self._errors['departure_date'] = \
                    self.error_class(['Departure date is not specified'])        

        return cleaned_data


class TrackedWayDetailForm(TrackedWayCreateForm):
    pass


class HistorySubscriptionForm(SubmitFormMixin, forms.ModelForm):
    class Meta:
        model = models.HistorySubscription
        exclude = ('history',)
