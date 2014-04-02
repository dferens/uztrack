from django import template
from django.template.defaultfilters import stringfilter

from ..utils import WEEKDAYS


register = template.Library()

@register.filter
@stringfilter
def short_day_name(value):
    return WEEKDAYS.get(value, 'None')
