from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class SubmitForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        return super(SubmitForm, self).__init__(*args, **kwargs)
