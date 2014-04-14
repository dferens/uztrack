import calendar
import datetime

from django.utils import timezone


class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def total_seconds(td):
    """
    Compatibility fix for < 2.7

    :type td: :class:`datetime.timedelta`
    """
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6


def date_to_ua_timestamp(date_or_dt):
    # because ``datetime.datetime`` subclasses ``datetime.date``
    if type(date_or_dt) is  datetime.date:
        dt = timezone.datetime.combine(date_or_dt, datetime.time())
        return calendar.timegm(dt.timetuple())
    else:
        dt = timezone.make_aware(date_or_dt, timezone.get_default_timezone())
        return calendar.timegm(dt.utctimetuple())
