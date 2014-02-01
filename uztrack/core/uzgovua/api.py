import datetime

from core.utils import DotDict

from . import raw


class Api(object):

    _raw_api = raw.RawApi()

    def _convert_station_id(self, station_id):
        return int(station_id)

    def _convert_time(self, date_format):
        return datetime.datetime(year=date_format['year'],
                                 month=date_format['mon'],
                                 day=date_format['mday'],
                                 hour=date_format['hours'],
                                 minute=date_format['minutes'],
                                 second=date_format['seconds']) 

    def _convert_station(self, station_data):
        return DotDict({
            'station_id': self._convert_station_id(station_data['station_id']),
            'station': station_data['station'],
            'time': self._convert_time(station_data['date_format'])
        })

    def _convert_types(self, train_types):
        result = DotDict(total=sum([x['places'] for x in train_types]))
        for train_type in train_types:
            result[train_type['title']] = train_type['places']
        return result

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
                tracked_way.departure_date, tracked_way.start_time)

        result = DotDict(trains=[])
        json_data = self._raw_api.get_stations_routes(*args, token=token)
        for train_data in json_data['value']:
            result.trains.append(DotDict(
                name=train_data['num'],
                category=train_data['category'],
                model=train_data['model'],
                places=self._convert_types(train_data['types']),
                departure=self._convert_station(train_data['from']),
                arrival=self._convert_station(train_data['till']),
            ))

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


