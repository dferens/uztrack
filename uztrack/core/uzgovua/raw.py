import re
import requests
import datetime
from urlparse import urljoin

from . import utils
from .exceptions import *


HOST_URL = 'http://booking.uz.gov.ua/'


class Access(object):
    pat_token = re.compile(r'"\\\\\\""\+(?P<token>[$_.+]*)\+')
    encoded_token_subs = {
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
    URLS = {
        'root': HOST_URL,
        'routes': urljoin(HOST_URL, 'purchase/search'),
    }

    @utils.host_available
    def __enter__(self):
        response = requests.get(HOST_URL)
        self.token = self.get_token(response)
        self.cookies = response.cookies
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del self.token
        del self.cookies

        if exc_type:
            raise exc_value

    @utils.host_available
    def get_stations_trains(self,
                            station_id_from, station_id_till,
                            departure_date=None, departure_start_time=None):
        """
        :type station_id_from: int
        :type station_id_till: int
        :type departure_date: date | datetime
        :type departure_start_time: time | datetime
        """
        if self.token is None or self.cookies is None:
            raise APIException('Use it inside context manager')

        if departure_date is None:
            departure_date = datetime.date.today()

        if departure_start_time is None:
            departure_start_time = datetime.time(0, 0)

        data = {
            'station_id_from': station_id_from,
            'station_id_till': station_id_till,
            'date_dep': departure_date.strftime('%d.%m.%Y'),     # 05.10.2013
            'time_dep': departure_start_time.strftime('%H:%M'),  # 12:34
        }
        headers = {
            'GV-Ajax': 1,
            'GV-Token': self.token,
            'GV-Referer': HOST_URL
        }
        cookies = self.cookies
        response = requests.post(self.URLS['routes'],
                                 data=data,
                                 headers=headers,
                                 cookies=cookies)

        utils.check_content_type(response, 'json')
        response = response.json()
        utils.check_json_error(response)
        return response

    @utils.host_available
    def get_token(self, response=None):
        if response is None:
            content = requests.get(HOST_URL).content
        else:
            content = response.content

        token_encoded = self.pat_token.search(content).group('token')
        token_symbols_encoded = [x.split('$$_.')[1] for x in token_encoded.split('+')]
        token_symbols_decoded = [self.encoded_token_subs[x] for x in token_symbols_encoded]
        token_decoded = ''.join(token_symbols_decoded)
        return token_decoded


@utils.host_available
def get_station_id(station_name):
    url = urljoin(HOST_URL, 'purchase/station/')
    url = urljoin(url, station_name)
    response = requests.post(url)

    utils.check_content_type(response, 'json')
    response = response.json()
    utils.check_json_error(response)
    return response
