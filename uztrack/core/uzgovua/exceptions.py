import re

from django.utils import timezone


class ApiException(Exception):

    def __init__(self, message):
        super(ApiException, self).__init__(message)


class BannedApiException(ApiException):

    def __init__(self, message):
        minutes = int(re.search(r'(\d+)', message).group(0))
        self.made_on = timezone.now()
        self.banned_for(timezone.timedelta(minutes=minutes))
        super(BannedApiException, self).__init__(message)
