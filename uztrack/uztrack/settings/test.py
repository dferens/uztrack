from .base import *
from core.utils.settings import settings

@settings(to_dict=True)
class DATABASES(object):
    def default(self): return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }

@settings
class OwnApps(object):
    def POLLER_DRY_RUN(self): return True
    def POLLER_AUTOSTART(self): return False
    def POLLER_AUTOSTART_NEW(self): return False


@settings
class Logging(Logging):
    def LOGGING(self):
        result = Logging.LOGGING(self)
        for logger in result['loggers']:
            result['loggers'][logger]['level'] = 'ERROR'

        return result
