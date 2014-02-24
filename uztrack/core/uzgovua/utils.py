import requests

from .exceptions import *


def check_content_type(response, check_for):
    content_type = response.headers['content-type']
    if check_for not in content_type:
        raise ApiException('Got "%s" response, expected "%s"' % (content_type, check_for))


def host_available(func):
    def decorated(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except requests.ConnectionError as e:
            host = e.args[0].pool.host
            raise ApiException('Host is down or not known: %s' % host)
        else:
            return result
    return decorated
