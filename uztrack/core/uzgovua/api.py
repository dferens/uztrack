import datetime

from core.utils import DotDict

from . import raw
from .exceptions import *


class Api(object):

    @classmethod
    def _convert_station_id(cls, station_id):
        return int(station_id)

    @classmethod
    def _convert_time(cls, date_format):
        return datetime.datetime(year=date_format['year'],
                                 month=date_format['mon'],
                                 day=date_format['mday'],
                                 hour=date_format['hours'],
                                 minute=date_format['minutes'],
                                 second=date_format['seconds']) 

    @classmethod
    def _convert_station(cls, station_data):
        return DotDict({
            'station_id': cls._convert_station_id(station_data['station_id']),
            'station': station_data['station'],
            'time': cls._convert_time(station_data['date_format'])
        })

    @classmethod
    def _convert_types(cls, types):
        result = DotDict({
            'total': sum([x['places'] for x in types]),    
        })
        for t in types:
            result[t['title']] = t['places']

    @classmethod
    def get_station_id(cls, station_name):
        json_data = raw.get_station_id(station_name)
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

    @classmethod
    def get_stations_trains(cls, station_id_from, station_id_till,
                            departure_date=None, departure_start_time=None,
                            access=None):
        if access is None:
            return get_stations_trains(station_id_from, station_id_till,
                                       departure_date, departure_start_time,
                                       access=Access())
        else:
            result = DotDict()
            try:
                json_data = access.get_stations_trains(station_id_from, station_id_till,
                                                       departure_date, departure_start_time,
                                                       access)
            except UzGovUaAPIException as e:
                pass                
            else:
                result.trains = []
                for train_data in json_data['value']:
                    train = DotDict()
                    train.name = train_data['num']
                    train.category = train_data['category']
                    train.model = train_data['model']
                    train.places = cls._convert_types(train_data['types'])
                    train.departure = cls._convert_station(train_data['from'])
                    train.arrival = cls._convert_station(train_data['till'])
                    result.trains.append(train)

            return result

