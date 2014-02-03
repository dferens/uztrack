import datetime

from django.utils import timezone

from core.utils import DotDict

from . import raw, data


class Api(object):

    _raw_api = raw.RawApi()

    def get_station_id(self, station_name):
        """
        Returns uz.gov.ua station id for given station name.

        :type station_name: str or unicode
        :rtype: int or None
        """
        json_data = self._raw_api.get_station_id(station_name)
        results = json_data['value']
        if len(results) == 0:
            return None
        else:
            for result_item in results:
                station_id, title = result_item['station_id'], result_item['title']

                if title == station_name:
                    # Exact match
                    return station_id
            else:
                # Closest match
                return results[0]['station_id']

    def get_stations_routes(self, way_history, token=None):
        token = raw.Token() if token is None else token
        tracked_way = way_history.tracked_way
        args = (tracked_way.way.station_id_from, tracked_way.way.station_id_to,
                way_history.departure_date, tracked_way.start_time)

        json_data = self._raw_api.get_stations_routes(*args, token=token)
        return data.StationsRoutes._parse(json_data)


class SmartApi(Api):
    # Experimental
    _token_ttl = datetime.timedelta(minutes=15)

    def __init__(self):
        self._token = None
        self._token_guessed_die = timezone.now()

    @property
    def token(self):
        now = timezone.now()
        if now  > self._token_guessed_die:
            self._token = raw.Token()
            self._token_guessed_die = now + self._token_ttl

        return self._token

    def get_stations_routes(self, way_history):
        super_method = super(SmartApi, self).get_stations_routes
        return super_method(way_history, token=self.token)
