import re

from django.utils import timezone


class ApiException(Exception):

    def __init__(self, message):
        pass


class BannedApiException(ApiException):

    def __init__(self, message):
        minutes = int(re.search(r'(\d+)', message).group(0))
        self.made_on = timezone.now()
        self.banned_for(timezone.timedelta(minutes=minutes))
        super(BannedApiException, self).__init__(message)


class ParseException(Exception):
    def __init__(self, *args):
        if len(args) == 2 and isinstance(args[0], BaseException):
            self.caused_by, obj  = args
            message = 'Exception occured during parse: \n%s' % self.caused_by
            message += '\nObject: %s' % obj
        elif len(args) == 3:
            obj, expected_type, got_type = args
            message = 'Expected type %s got %s:\nObject:%s'
            message = message % (expected_type, got_type, obj)

        super(ParseException, self).__init__(message)
