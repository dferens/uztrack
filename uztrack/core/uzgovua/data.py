from datetime import datetime

from schematics.exceptions import ConversionError
from schematics.models import Model
from schematics.types import BaseType, IntType, StringType, BooleanType, DateTimeType
from schematics.types.compound import ListType, ModelType
from schematics.transforms import *


class NonStrictModel(Model):

    def __init__(self, raw_data=None, deserialize_mapping=None):
        self._initial = {} if raw_data is None else raw_data
        self._data = self.convert(self._initial, strict=False,
                                  mapping=deserialize_mapping)


class TimestampDateTimeType(DateTimeType):
    """
    Uses unix timestamp to create :class:`datetime.datetime` object.
    """
    def __init__(self, **kwargs):
        super(TimestampDateTimeType, self).__init__(**kwargs)

    def to_native(self, value):
        if isinstance(value, int):
            return datetime.fromtimestamp(value)
        raise ConversionError(self.messages['parse'].format(value))


class SeatsData(Model):
    name = StringType(required=True, serialized_name='letter')
    full_name = StringType(required=True, serialized_name='title')
    seats_count = IntType(required=True, serialized_name='places')


class StationData(Model):
    id = IntType(required=True, serialized_name='station_id')
    name = StringType(required=True, serialized_name='station')
    date = TimestampDateTimeType(required=True)
    _date2 = StringType(serialized_name='src_date')


class RouteTrain(Model):
    code = StringType(required=True, serialized_name='num')
    category = IntType(required=True)
    station_from = ModelType(StationData, required=True, serialized_name='from')
    station_till = ModelType(StationData, required=True, serialized_name='till')
    model = IntType(required=True)
    seat_types = ListType(ModelType(SeatsData),
                          required=True,
                          serialized_name='types',
                          default=list)

    @property
    def seats_count(self):
        return sum(x.seats_count for x in self.seat_types)

    def __iter__(self):
        return self.seat_types.__iter__()

    def __getitem__(self, key):
        return self.seat_types[key]

    def __len__(self):
        return len(self.seat_types)


class RouteTrains(NonStrictModel):
    trains = ListType(ModelType(RouteTrain),
                      required=True,
                      serialized_name='value', 
                      default=list)

    @property
    def seats_count(self):
        return sum(x.seats_count for x in self.trains)

    def __iter__(self):
        return self.trains.__iter__()

    def __getitem__(self, key):
        return self.trains[key]

    def __len__(self):
        return len(self.trains)
