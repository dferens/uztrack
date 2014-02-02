class APIException(Exception):
    pass


class UzGovUaAPIException(Exception):
    def __init__(self, url, message):
        self.url = url
        message = '(%s): %s' % (url, message)
        super(UzGovUaAPIException, self).__init__(message)


class ParseException(Exception):
    def __init__(self, caused_by):
        super(ParseException, self).__init__(caused_by)