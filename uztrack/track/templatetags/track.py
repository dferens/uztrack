from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from ..utils import WEEKDAYS


register = template.Library()

@register.filter
@stringfilter
def short_day_name(value):
    return WEEKDAYS.get(value, 'None')


@register.filter
def time_24h(value):    
    return mark_safe('&infin;' if value is None else value.strftime('%H:%M'))
