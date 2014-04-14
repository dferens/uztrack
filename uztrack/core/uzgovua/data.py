from datetime import datetime
from decimal import Decimal

from schematics.exceptions import ConversionError
from schematics.models import Model
from schematics.types import BaseType, IntType, StringType, BooleanType, \
                             DecimalType, DateTimeType
from schematics.types.compound import ListType, ModelType
from schematics.transforms import *

from core.utils import date_to_ua_timestamp


def is_raw(data_dict):
    if data_dict:
        for key in ('data', 'value', 'error'):
            if key not in data_dict:
                return False
        return True
    return False


class NonStrictModel(Model):

    def __init__(self, raw_data=None, deserialize_mapping=None):
        self._initial = {} if raw_data is None else raw_data
        self._data = self.convert(self._initial, strict=False,
                                  mapping=deserialize_mapping)


class TimestampDateTimeType(DateTimeType):
    """
    Uses unix timestamp to create :class:`datetime.datetime` object.
    """
    def to_native(self, value):
        if isinstance(value, int):
            return datetime.fromtimestamp(value)
        raise ConversionError(self.messages['parse'].format(value))    

    def to_primitive(self, value):
        return date_to_ua_timestamp(value)


class CurrencyDecimalType(DecimalType):
    def to_native(self, value):
        if isinstance(value, int):
            return Decimal(value) / Decimal(100)
        raise ConversionError(self.messages['parse'].format(value))

    def to_primitive(self, value):
        return int(value * 100)


class CoachSeats(Model):
    number = IntType(required=True,serialized_name='num')
    allow_bonus = BooleanType(required=True)
    has_bedding = BooleanType(required=True, serialized_name='hasBedding')
    seats_count = IntType(required=True, min_value=1,
                          serialized_name='places_cnt')
    reserve_price = CurrencyDecimalType(required=True)
    _prices = ListType(CurrencyDecimalType, required=True, min_size=1,
                       serialized_name='prices')

    def __init__(self, dict_data=None):
        if 'coach_type_id' in dict_data:
            dict_data.pop('coach_type_id', None)
            dict_data.pop('services', None)
            dict_data['prices'] = dict_data.pop('prices', {}).values()
        super(CoachSeats, self).__init__(dict_data)

    @property
    def price(self):
        return min(self._prices)


class SeatsData(Model):
    name = StringType(required=True, serialized_name='letter')
    full_name = StringType(required=True, serialized_name='title')
    seats_count = IntType(required=True, serialized_name='places')
    coaches = ListType(ModelType(CoachSeats), required=False)

    @property
    def price(self):
        if self.coaches:
            return min(c.price for c in self.coaches)
        return None


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


class RouteTrains(NonStrictModel):
    trains = ListType(ModelType(RouteTrain),
                      required=True,
                      default=list)

    @classmethod
    def _crop(cls, data):
        data['trains'] = data.pop('value', [])
        data.pop('error', None)
        data.pop('data', None)

    @property
    def seats_count(self):
        return sum(x.seats_count for x in self.trains)

    def __init__(self, dict_data=None):
        if is_raw(dict_data): self._crop(dict_data)
        NonStrictModel.__init__(self, dict_data)


class RouteCoaches(Model):

    coaches = ListType(ModelType(CoachSeats),
                       required=True,
                       default=list)

    @classmethod
    def _crop(cls, data):
        data['coaches'] = data['value'].pop('coaches', [])
        data.pop('value')
        data.pop('error')
        data.pop('data')

    def __init__(self, dict_data=None):
        if is_raw(dict_data): self._crop(dict_data)
        super(RouteCoaches, self).__init__(dict_data)

    @property
    def price(self):
        return min(c.price for c in self.coaches)
