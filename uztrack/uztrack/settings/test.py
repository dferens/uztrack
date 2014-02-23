from .base import *
from .utils import *


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
    def POLLER_AUTOSTART(self): return False
    def POLLER_AUTOSTART_NEW(self): return False
