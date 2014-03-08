from django.utils import timezone


def total_seconds(td):
    """
    Compatibility fix for < 2.7

    :type td: :class:`datetime.timedelta`
    """
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
