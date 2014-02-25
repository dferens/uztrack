# -*- coding: utf-8 -*-
import datetime

from django.utils import timezone

from core.utils import DotDict

from . import raw, data
from .exceptions import ApiException, BannedApiException


class Api(object):

    _raw_api = raw.RawApi()

    def _check_for_errors(self, json_data):
        if json_data['error']:
            message = json_data['value']
            # Too many requests
            if message.startswith(u'Перевищено кількість запитів'):
                ExceptionClass = BannedApiException
            # Nothing found
            elif message.startswith(u'За заданими Вами значенням нічого не знайдено'):
                return
            # Service is temporarily unavailable
            elif message.startswith(u'Сервіс тимчасово недоступний'):
                return
            # Unexpected error
            else:
                ExceptionClass = ApiException

            raise ExceptionClass(message)

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
        self._check_for_errors(json_data)
        return data.StationsRoutes._parse(json_data)


class SmartApi(Api):
    # Experimental
    _token_ttl = datetime.timedelta(minutes=15)

    def __init__(self):
        self._token = None
        self._token_guessed_die = timezone.now()

    def _refresh_token(self, now=None):
        self._token = raw.Token()
        now = timezone.now() if now is None else now
        self._token_guessed_die = now + self._token_ttl

    @property
    def token(self):
        now = timezone.now()
        if now > self._token_guessed_die:
            self._refresh_token(now)

        return self._token

    def get_stations_routes(self, way_history):
        super_method = super(SmartApi, self).get_stations_routes
        try:
            first_try = super_method(way_history, token=self.token)
        except BannedApiException, e:
            self._refresh_token()
            try:
                second_try = super_method(way_history, token=self.token)
            except BannedApiException, e:
                logger.error('could not pass site protection, '
                             'banned for %s minutes', e.banned_for)
            else:
                logger.info('passed site protection')
                return second_try
        else:
            return first_try
