from datetime import date

from django.conf import settings

from .models import TrackedWayDayHistory, TrackedWayDayHistorySnapshot


def get_closest_histories(tracked_way):
    till_date = date.today() + settings.TICKETS_SEARCH_RANGE
    dates = tracked_way.next_dates(till_date)
    found_histories = TrackedWayDayHistory.objects.filter(departure_date__in=dates).all()
    found_dates = found_histories.values_list('departure_date', flat=True)
    not_found_dates = filter(lambda d: d not in found_dates, dates)
    histories_list = list(found_histories)
    for not_found_date in not_found_dates:
        histories_list.append(TrackedWayDayHistory.objects
                                                  .create(tracked_way=tracked_way,
                                                          departure_date=not_found_date))
    return histories_list


def create_snapshot(history, stations_routes):
    args = dict(history=history,
                total_places_count=stations_routes.seats_count,
                snapshot_data=stations_routes._raw)
    return TrackedWayDayHistorySnapshot.objects.create(**args)
