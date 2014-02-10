from django.utils import timezone


def get_last_snapshot_elapsed(history):
    last_snapshot_datetime = history.snapshots.last().made_on
    return timezone.now() - last_snapshot_datetime
