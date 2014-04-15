# -*- coding: utf-8 -*-
import datetime
import functools
import logging

import requests
from urlparse import urljoin

from django.utils import timezone

from core.utils import date_to_ua_timestamp
from . import exceptions, raw
from .data import RouteTrains, RouteCoaches


logger = logging.getLogger(__name__)


class RawApi(object):

    _URLS = {
        'station': urljoin(raw.HOST_URL, 'purchase/station/'),
        'search_routes': urljoin(raw.HOST_URL, 'purchase/search/'),
        'get_coaches': urljoin(raw.HOST_URL, 'purchase/coaches/')
    }

    NOT_FOUND = (
        u'По заданому Вами напрямку поїздів немає',
        u'За заданими Вами значенням нічого не знайдено.'
    )
    NOT_AVAILABLE = (
        u'Сервіс тимчасово недоступний',
        u'Попередження. Повторіть, будь ласка, свій запит. Сервер не може обслужити Вас в даний момент'
    )
    BANNED = u'Перевищено кількість запитів'

    def _check_for_errors(self, json_data):
        if json_data['error']:
            code = json_data['value']
            if code in self.NOT_FOUND:
                raise exceptions.NothingFoundException()
            elif code in self.NOT_AVAILABLE:
                raise exceptions.ServiceNotAvailableException()
            elif self.BANNED in code:
                raise exceptions.BannedApiException(code)
            else:
                raise exceptions.ApiException(code)

    def _require_token(self, token):
        if token is None:
            raise exceptions.TokenRequiredException()

    def get_station_id(self, station_name):
        """
        Returns uz.gov.ua station id for given station name.

        :type station_name: str or unicode
        :rtype: int or None
        """
        url = urljoin(self._URLS['station'], station_name)
        json_data = requests.post(url).json()
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

    def get_coaches(self, station_id_from, station_id_to,
                          departure_date, train_code, coach_type, token=None):
        self._require_token(token)
        url = self._URLS['get_coaches']
        data = {'station_id_from': station_id_from,
                'station_id_till': station_id_to,
                'date_dep': date_to_ua_timestamp(departure_date),
                'train': train_code,
                'coach_type': coach_type}
        data.update(model=0, round_trip=0, another_ec=0)
        json_data = token.patch_request(requests.post, url, data=data).json()
        self._check_for_errors(json_data)
        return json_data

    def get_stations_routes(self, station_id_from, station_id_to,
                                  departure_date, start_time, token=None):
        self._require_token(token)
        url = self._URLS['search_routes']
        data = {'station_id_from': station_id_from,
                'station_id_till': station_id_to,
                'date_dep': departure_date.strftime('%d.%m.%Y'),
                'time_dep': start_time.strftime('%H:%M')}
        json_data = token.patch_request(requests.post, url, data=data).json()
        self._check_for_errors(json_data)
        return json_data


class Api(RawApi):    

    def get_stations_routes(self, station_id_from, station_id_to,
                                  departure_date, start_time, token=None):
        args = station_id_from, station_id_to, departure_date, start_time
        try:
            json_data = super(Api, self).get_stations_routes(*args, token=token)
        except exceptions.NothingFoundException:
            return RouteTrains()
        else:
            return RouteTrains(json_data)

    def get_coaches(self, station_id_from, station_id_to,
                          departure_date, train_code, coach_type, token=None):
        args = station_id_from, station_id_to, departure_date, train_code, coach_type
        json_data = super(Api, self).get_coaches(*args, token=token)
        return RouteCoaches(json_data)


def handle_ban(method):
    @functools.wraps(method)
    def decorated(self, *args, **kwargs):
        try:
            first_try = method(self, *args, **kwargs)
        except exceptions.BannedApiException, e:
            self._refresh_token()
            try:
                second_try = method(self, *args, **kwargs)
            except exceptions.BannedApiException, e:
                logger.error('could not pass site protection, '
                             'banned for %s minutes', e.banned_for)
                raise e
            else:
                logger.info('passed site protection')
                return second_try
        else:
            return first_try

    return decorated


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

    @handle_ban
    def get_stations_routes(self, station_id_from, station_id_to,
                                  departure_date, start_time):
        super_method = super(SmartApi, self).get_stations_routes
        return super_method(station_id_from, station_id_to,
                            departure_date, start_time, token=self.token)


    @handle_ban
    def get_coaches(self, station_id_from, station_id_to,
                          departure_date, train_code, coach_type):
        super_method = super(SmartApi, self).get_coaches
        return super_method(station_id_from, station_id_to, departure_date,
                            train_code, coach_type, token=self.token)
