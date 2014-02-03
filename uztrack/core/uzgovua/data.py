from datetime import datetime
from operator import attrgetter

from .exceptions import ParseException


"""
This classes describes api objects.
"""

class ParsedObject(object):

    def _post_parse(self):
        raise NotImplementedError

    @classmethod
    def _parse(cls, data_dict):
        raise NotImplementedError

    @classmethod
    def _check_type(cls, *args):
        expected_type = args[-1]
        for obj in args[:-1]:
            if not isinstance(obj, expected_type):
                raise ParseException(obj, expected_type, type(obj))


class StationsRoutes(ParsedObject):
    class RouteTrainData(ParsedObject):
        """
        Parses route data by specific train, example:

            value = [{
                "category":0,
                 "from":{ ... },
                 "till":{ ... },
                 "num":"175\u0428",
                 "model":0,
                 "types":[...],
                },]
        """
        class StationData(ParsedObject):
            """
            Parses station data, example:

                from: {
                    "date":1392352200,
                    "station":"\u041a\u0438\u0457\u0432-...",
                    "src_date":"2014-02-14 06:30:00",
                    "station_id":"2200001"
                }
            """
            SRC_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
            @classmethod
            def _parse(cls, station_dict):
                try:
                    id = int(station_dict['station_id'])
                    name = unicode(station_dict['station'])
                    date = datetime.strptime(station_dict['src_date'], cls.SRC_DATE_FORMAT)
                except Exception, e:
                    raise ParseException(e)
                else:
                    return cls(id, name, date)

            def __unicode__(self):
                return u'%s' % (self.name)

            def __init__(self, id, name, date):
                self.id = id
                self.name = name
                self.date = date                

        class SeatsData(ParsedObject):
            """
            Parses seats data, example:

                types = [{
                   "places":34,
                   "letter":"\u04211",
                   "title":"\u0421\u0438\u0434\u044f\u0447\u0438\u0439 \u043f\u0435\u0440\u0448\u043e\u0433\u043e \u043a\u043b\u0430\u0441\u0443"
                },]
            """
            @classmethod
            def _parse(cls, seats_dict):
                try:
                    short_name = seats_dict['letter']
                    full_name = seats_dict['title']
                    count = int(seats_dict['places'])
                except Exception, e:
                    raise ParseException(e)
                else:
                    cls._check_type(short_name, full_name, basestring)
                    return cls(short_name, full_name, count)

            def __unicode__(self):
                return u'%s(%d)' % (self.short_name, self.count)

            def __init__(self, short_name, full_name, count):
                self.short_name = short_name
                self.full_name = full_name
                self.count = count

        @classmethod
        def _parse(cls, route_dict):
            cls._check_type(route_dict, dict)
            try:
                code = unicode(route_dict['num'])
                category = int(route_dict['category'])
                model = int(route_dict['model'])
                station_from_dict = route_dict['from']
                station_to_dict = route_dict['till']
                seats_list = route_dict['types']
            except Exception, e:
                raise ParseException(e)
            else:
                cls._check_type(station_from_dict, station_to_dict, dict)
                cls._check_type(seats_list, list)
                args = (category, code, model)
                kwargs = {
                    'station_from': cls.StationData._parse(station_from_dict),
                    'station_to': cls.StationData._parse(station_to_dict),
                }
                route_train = cls(*args, **kwargs)
                for seats_dict in seats_list:
                    cls._check_type(seats_dict, dict)
                    route_train.seats.append(cls.SeatsData._parse(seats_dict))

                route_train._post_parse()

                return route_train

        def __unicode__(self):
            return u'#%s (%d) ' % (self.code, self.seats_count)

        def __init__(self, category, code, model, station_from=None, station_to=None):
            self.category = category
            self.station_from = station_from
            self.station_to = station_to
            self.code = code
            self.model = model
            self.seats = []
            self.seats_count = None

        def _post_parse(self):
            self.seats_count = sum(map(attrgetter('count'), self.seats))

        def __iter__(self):
            return self.seats.__iter__()

    @classmethod
    def _parse(cls, stations_routes_dict):
        try:
            root = stations_routes_dict['value']
        except KeyError, e: 
            raise ParseException(e, root)
        else:
            cls._check_type(root, list)
            stations_routes = cls()
            for route_dict in root:
                route_train = cls.RouteTrainData._parse(route_dict)
                stations_routes.trains.append(route_train)

            stations_routes._post_parse()
            stations_routes._raw = stations_routes_dict

            return stations_routes

    def __init__(self):
        self.trains = []
        self.seats_count = None
        self._raw = None
        self.station_from = self.station_to = None

    def __iter__(self):
        return self.trains.__iter__()

    def __unicode__(self):
        return u'%s-%s trains=%d seats=%d' % (self.station_from, self.station_to,
                                              len(self.trains), self.seats_count)
     
    def _post_parse(self):
        self.seats_count = sum(map(attrgetter('seats_count'), self.trains))
        if self.trains:
            self.station_from = self.trains[0].station_from
            self.station_to = self.trains[0].station_to
