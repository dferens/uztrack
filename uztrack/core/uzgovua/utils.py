import requests

from .exceptions import *


def check_content_type(response, check_for):
    content_type = response.headers['content-type']
    if check_for not in content_type:
        raise APIException('Got "%s" response, expected "%s"' % (content_type, check_for))


def check_json_error(json_response):
    if json_response['error']:
        raise UzGovUaAPIException('Error occured: %s' % json_response['error'])


def host_available(func):
    def decorated(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except requests.ConnectionError as e:
            host = e.args[0].pool.host
            raise APIException('Host is down or not known: %s' % host)
        else:
            return result
    return decorated
