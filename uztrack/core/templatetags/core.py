import re
from datetime import datetime

from django import template
from django.template import defaultfilters
from django.utils import timezone
from django.utils.html import avoid_wrapping
from django.utils.translation import pgettext, ugettext, ungettext_lazy


register = template.Library()


@register.filter
def naturaldate(value):
    today = timezone.now().date()
    if  value == today:
        return 'today'
    else:
        difference = value - today
        if difference.days < 7:
            template = ungettext_lazy('%d day', '%d days')
            result = avoid_wrapping(template % difference.days)            
        else:
            result = defaultfilters.timeuntil(value)

        return pgettext('naturaltime', result)


@register.filter
def timestamp(value):
    return datetime.fromtimestamp(value)
