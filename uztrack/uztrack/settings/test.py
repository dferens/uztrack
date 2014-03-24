from classsettings import Settings, Config

from .base import *


class DATABASES(Config):
    def default(self): return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }

class OwnApps(Settings):
    def POLLER_DRY_RUN(self): return True
    def POLLER_AUTOSTART(self): return False
    def POLLER_AUTOSTART_NEW(self): return False

class Logging(Logging):
    def LOGGING(self):
        result = super(type(self), self).LOGGING()
        for logger in result['loggers']:
            result['loggers'][logger]['level'] = 'CRITICAL'

        return result
