from django.utils import timezone


def get_last_snapshot_elapsed(history):
    last_snapshot_datetime = history.snapshots.last().made_on
    return timezone.now() - last_snapshot_datetime


def total_seconds(td):
    """
    Compatibility fix for < 2.7

    :type td: :class:`datetime.timedelta`
    """
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
