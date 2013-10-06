from dateutil import rrule


WEEKDAYS = ('Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday')


def get_dateutil_weekday(weekday):
    return getattr(rrule, weekday[:2].upper())