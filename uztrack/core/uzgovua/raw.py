import re
import datetime
import functools

import requests

from . import exceptions


HOST_URL = 'http://booking.uz.gov.ua/'


class Token(object):
    """
    Site sends obfuscated JS code which contains secret hex string - this token.
    This class decodes changing part of that code into string, without touching
    js interpreter.
    """
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
    _TOKEN_SOURCE_URL = HOST_URL

    def __init__(self):
        response = requests.get(self._TOKEN_SOURCE_URL)
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
        """
        Additional http headers we need to pass for making specific json requests.
        """
        return {'GV-Ajax': 1,
                'GV-Token': self.token,
                'GV-Referer': self._TOKEN_SOURCE_URL}

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
