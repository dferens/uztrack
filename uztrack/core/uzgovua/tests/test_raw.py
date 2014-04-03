import datetime
import mock

from django.test import TestCase
from django.utils import timezone

from .. import exceptions, raw


class ResponseMock(object):

    def __init__(self, content, cookies=None):
        self.content = content
        self.cookies = cookies


class TokenMock(raw.Token):

    def __init__(self, decoded_token=None, cookies=None):
        object.__init__(self)
        self.token = decoded_token or 'decoded'
        self.cookies = cookies or 'cookies'


class TokenTestCase(TestCase):

    @mock.patch('core.uzgovua.raw.requests')
    def test_init(self, mock_requests):
        mock_encoded_token = '1e1839ddb30c7cd4dbb1644164da0bab'
        # '\' chars were replaced with '/' manually
        mock_content = (
        '<html>'
        '''_gaq.push(['_trackPageview']);$$_=~[];$$_={___:++$$_,$$$$:(![]+"")'''
        '''[$$_],__$:++$$_,$_$_:(![]+"")[$$_],_$_:++$$_,$_$$:({}+"")[$$_],$$_'''
        '''$:($$_[$$_]+"")[$$_],_$$:++$$_,$$$_:(!""+"")[$$_],$__:++$$_,$_$:++'''
        '''$$_,$$__:({}+"")[$$_],$$_:++$$_,$$$:++$$_,$___:++$$_,$__$:++$$_};$'''
        '''$_.$_=($$_.$_=$$_+"")[$$_.$_$]+($$_._$=$$_.$_[$$_.__$])+($$_.$$=($'''
        '''$_.$+"")[$$_.__$])+((!$$_)+"")[$$_._$$]+($$_.__=$$_.$_[$$_.$$_])+('''
        '''$$_.$=(!""+"")[$$_.__$])+($$_._=(!""+"")[$$_._$_])+$$_.$_[$$_.$_$]'''
        '''+$$_.__+$$_._$+$$_.$;$$_.$$=$$_.$+(!""+"")[$$_._$$]+$$_.__+$$_._+$'''
        '''$_.$+$$_.$$;$$_.$=($$_.___)[$$_.$_][$$_.$_];$$_.$($$_.$($$_.$$+"/"'''
        '''"+(![]+"")[$$_._$_]+$$_._$+$$_.$$__+$$_.$_$_+(![]+"")[$$_._$_]+"//'''
        '''"+$$_.__$+$$_._$_+$$_._$$+$$_.__+$$_._$+"//"+$$_.__$+$$_.$$_+$$_._'''
        '''$_+$$_.$_$_+"//"+$$_.__$+$$_.$__+$$_.$$$+$$_.$$$_+".//"+$$_.__$+$$'''
        '''_.$$_+$$_._$$+$$_.$$$_+$$_.__+"//"+$$_.__$+$$_.__$+$$_.__$+$$_.__+'''
        '''$$_.$$$_+"//"+$$_.__$+$$_.$_$+$$_.$_$+"(///"//"+$$_.__$+$$_.$__+$$'''
        '''_.$$$+"//"+$$_.__$+$$_.$$_+$$_.$$_+"-"+$$_.__+$$_._$+"//"+$$_.__$+'''
        '''$$_.$_$+$$_._$$+$$_.$$$_+"//"+$$_.__$+$$_.$_$+$$_.$$_+"///",//"+$$'''
        '''_.$__+$$_.___+"///""+$$_.__$+$$_.$$$_+$$_.__$+$$_.$___+$$_._$$+$$_'''
        '''.$__$+$$_.$$_$+$$_.$$_$+$$_.$_$$+$$_._$$+$$_.___+$$_.$$__+$$_.$$$+'''
        '''$$_.$$__+$$_.$$_$+$$_.$__+$$_.$$_$+$$_.$_$$+$$_.$_$$+$$_.__$+$$_.$'''
        '''$_+$$_.$__+$$_.$__+$$_.__$+$$_.$$_+$$_.$__+$$_.$$_$+$$_.$_$_+$$_._'''
        '''__+$$_.$_$$+$$_.$_$_+$$_.$_$$+"///");"+"/"")())();'''
        '</html>'.replace('/', '\\'))
        mock_cookies = 'Some cookies'
        resp = ResponseMock(mock_content, mock_cookies)
        mock_requests.get.return_value = resp

        token = raw.Token()
        self.assertEqual(token.token, mock_encoded_token)
        self.assertEqual(token.cookies, mock_cookies)

    def test_patch_request(self):
        token = TokenMock('decoded_token', 'cookies')
        mock_request_method = mock.MagicMock()

        token.patch_request(mock_request_method, 1, kwarg=2)
        self.assertEqual(mock_request_method.call_count, 1)
        self.assertEqual(mock_request_method.call_args[0], (1,))
        self.assertDictContainsSubset(
            {'GV-Token': token.token},
            mock_request_method.call_args[1]['headers']
        )
        mock_request_method.reset_mock()

        token.patch_request(mock_request_method, 1, headers={'one': 1})
        self.assertEqual(mock_request_method.call_count, 1)
        self.assertEqual(mock_request_method.call_args[0], (1,))
        self.assertDictContainsSubset(
            {'one': 1, 'GV-Token': token.token},
            mock_request_method.call_args[1]['headers']
        )
        mock_request_method.reset_mock()
