import re

from django.utils import timezone


class ApiException(Exception):
    pass


class TokenRequiredException(ApiException):
    pass


class BannedApiException(ApiException):
    """
    """
    def __init__(self, message):
        super(BannedApiException, self).__init__()
        minutes = int(re.search(r'(\d+)', message).group(0))
        self.made_on = timezone.now()
        self.banned_for = timezone.timedelta(minutes=minutes)


class ServiceNotAvailableException(ApiException):
    """
    Service is not responding.
    """
    pass


class NothingFoundException(ApiException):
    pass

