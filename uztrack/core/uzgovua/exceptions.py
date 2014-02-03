class APIException(Exception):
    pass


class UzGovUaAPIException(Exception):
    def __init__(self, url, message):
        self.url = url
        message = '(%s): %s' % (url, message)
        super(UzGovUaAPIException, self).__init__(message)


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
