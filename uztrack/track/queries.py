from django.conf import settings
from django.utils import timezone

from .models import TrackedWayDayHistory as History, \
                    TrackedWayDayHistorySnapshot as Snapshot


def get_closest_histories(tracked_way):
    """
    Returns collection of closest :class:`History` objects for a given way.
    Creates new records if needed.
    """
    closest_dates = tracked_way.next_dates(get_search_till_date())
    found_histories = History.objects.filter(departure_date__in=closest_dates)
    found_dates = found_histories.values_list('departure_date', flat=True)
    not_found_dates = filter(lambda d: d not in found_dates, closest_dates)
    histories_list = list(found_histories)
    for not_found_date in not_found_dates:
        histories_list.append(
            History.objects.create(tracked_way=tracked_way,
                                   departure_date=not_found_date)
        )
    return histories_list


def create_snapshot(history, stations_routes):
    """
    Creates :class:`Snapshot` snapshot from a given api call result.

    :type history: :class:`History`
    :type stations_routes: :class:`core.uzgovua.data.StationsRoutes`
    """
    return Snapshot.objects.create(history=history,
                                   total_places_count=stations_routes.seats_count,
                                   snapshot_data=stations_routes._raw)

def get_search_till_date():
    today = timezone.datetime.today().date()
    return today + settings.TICKETS_SEARCH_RANGE
