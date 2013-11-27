import re
import requests
import datetime
from urlparse import urljoin

from . import utils
from .exceptions import *


HOST_URL = 'http://booking.uz.gov.ua/'


class Token(object):
    
    _pat_token = re.compile(r'"\\\\\\""\+(?P<token>[$_.+]*)\+')
    _encoded_token_subs = {
        '_': 'u',
        '_$': 'o',
        '__': 't',
        '$$$$': 'f',
        '$$$_': 'e',
        '$$_$': 'd',
        '$$__': 'c',
        '$_$$': 'b',
        '$_$_': 'a',
        '$__$': '9',
        '$___': '8',
        '$$$': '7',
        '$$_': '6',
        '$_$': '5',
        '$__': '4',
        '_$$': '3',
        '_$_': '2',
        '__$': '1',
        '___': '0'
    }
    _URLS = {
        'token_source': HOST_URL,
    }

    def __init__(self):
        response = requests.get(self._URLS['token_source'])
        content = response.content
        token_encoded = self._pat_token.search(content).group('token')
        token_symbols_encoded = [x.split('$$_.')[1] for x in token_encoded.split('+')]
        token_symbols_decoded = [self._encoded_token_subs[x] for x in token_symbols_encoded]
        token_decoded = ''.join(token_symbols_decoded)

        self.token = token_decoded
        self.cookies = response.cookies

    def __unicode__(self):
        return u'<Access token "%s">' % self.token

    @property
    def access_headers(self):
        return {
            'GV-Ajax': 1,
            'GV-Token': self.token,
            'GV-Referer': self._URLS['token_source']
        }

    @property
    def access_cookies(self):
        return self.cookies

    def patch_request(self, request_method, *args, **kwargs):
        headers = kwargs.get('headers')
        if headers is None:
            kwargs['headers'] = self.access_headers
        else:
            kwargs['headers'].update(self.access_headers)

        kwargs['cookies'] = self.access_cookies
        return request_method(*args, **kwargs)


class RawApi(object):

    _URLS = {
        'station': urljoin(HOST_URL, 'purchase/station/'),
        'search_routes': urljoin(HOST_URL, 'purchase/search/'),
    }

    def get_stations_routes(self,
                            station_id_from, station_id_till,
                            departure_date, departure_start_time,
                            token=None):
        """
        :type station_id_from: int
        :type station_id_till: int
        :type departure_date: date | datetime
        :type departure_start_time: time | datetime
        """
        if token is None:
            raise APIException('Token is required')

        data = {
            'station_id_from': station_id_from,
            'station_id_till': station_id_till,
            'date_dep': departure_date.strftime('%d.%m.%Y'),     # 05.10.2013
            'time_dep': departure_start_time.strftime('%H:%M'),  # 12:34
        }
        response = token.patch_request(requests.post,
                                       self._URLS['search_routes'],
                                       data=data)
        return response.json()

    def get_station_id(station_name, token=None):
        url = urljoin(self._URLS['station'], station_name)
        response = requests.post(url)
        return response.json()