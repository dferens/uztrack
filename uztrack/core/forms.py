from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class SubmitFormMixin(object):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        return super(SubmitFormMixin, self).__init__(*args, **kwargs)
