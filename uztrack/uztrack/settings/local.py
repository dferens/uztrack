from os.path import join, normpath

from .base import *
from .utils import settings


@settings
class Administration(object):
    def DEBUG(self): return True
    def INTERNAL_IPS(self): return ('127.0.0.1',)

@settings
class Emails(object):
    def EMAIL_BACKEND(self):
        return 'django.core.mail.backends.console.EmailBackend'

@settings
class Databases(object):
    def DATABASES(self): return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': normpath(join(DJANGO_ROOT, 'default.db')),
                'USER': '',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '',
            }
        }

@settings
class Caches(object):
    def CACHES(self): return {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

@settings
class Celery(object):
    def BROKER_URL(self): return 'redis://localhost:6379/0'

@settings
class Apps(Apps):
    def THIRD_PARTY_APPS(self):
        return Apps.THIRD_PARTY_APPS(self) + (
            'debug_toolbar',
        )

@settings
class Routing(Routing):
    def MIDDLEWARE_CLASSES(self):
        return Routing.MIDDLEWARE_CLASSES(self) + (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )

@settings
class DebugToolbar(object):
    def DEBUG_TOOLBAR_CONFIG(self): return {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TEMPLATE_CONTEXT': True,
    }
