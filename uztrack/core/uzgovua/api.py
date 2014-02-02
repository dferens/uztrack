import datetime

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
        result = data.StationsRoutes._parse(json_data)
        return result


class ApiSession(Api):
    """
    Patches some json requests with generated token, use as context manager.
    """
    def __enter__(self):
        self.token = raw.Token()
        return self

    def __exit__(self, exc_type, exc_value, trace):
        del self.token

    def get_stations_routes(self, way_history):
        super_method = super(ApiSession, self).get_stations_routes
        return super_method(way_history, token=self.token)


