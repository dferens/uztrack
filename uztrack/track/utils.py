from collections import OrderedDict
from dateutil import rrule


WEEKDAYS = OrderedDict()
WEEKDAYS['Monday'] = 'Mo'
WEEKDAYS['Tuesday'] = 'Tu'
WEEKDAYS['Wednesday'] = 'We'
WEEKDAYS['Thursday'] = 'Th'
WEEKDAYS['Friday'] = 'Fr'
WEEKDAYS['Saturday'] = 'Sa'
WEEKDAYS['Sunday'] = 'Su'


def get_dateutil_weekday(weekday):
    return getattr(rrule, weekday[:2].upper())
