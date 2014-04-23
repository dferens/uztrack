from django.conf import settings
from django.utils import timezone

from .models import TrackedWayDayHistory as History, \
                    TrackedWayDayHistorySnapshot as Snapshot


def check_expired_histories():
    """
    Finds and sets ``active`` to ``False`` for each way history with expired
    departure date.
    """
    today = timezone.now().date()
    closed_count = (History.objects.filter(active=True,
                                           departure_date__lt=today)
                                   .update(active=False))
    return closed_count


def create_snapshot(history, stations_routes):
    """
    Creates :class:`Snapshot` snapshot from a given api call result.

    :type history: :class:`History`
    :type stations_routes: :class:`core.uzgovua.data.StationsRoutes`
    """
    return Snapshot.objects.create(history=history,
                                   total_places_count=stations_routes.seats_count,
                                   snapshot_data=stations_routes.to_primitive())

def get_search_till_date():
    today = timezone.datetime.today().date()
    return today + settings.TICKETS_SEARCH_RANGE


def patch_last_snapshots(histories):
    if histories:
      sql = 'SELECT * FROM %s WHERE id IN' \
            ' (SELECT max(id) FROM %s ' \
            '  WHERE history_id IN (%s) ' \
            '  GROUP BY history_id)'
      sql = sql % (Snapshot._meta.db_table, Snapshot._meta.db_table,
                   ','.join(str(h.id) for h in histories))
      snapshots = list(Snapshot.objects.raw(sql))
      histories_snapshots_map = {s.history_id: s for s in snapshots}
      for history in histories:
          history.last_snapshot = histories_snapshots_map.get(history.id)

    return histories
