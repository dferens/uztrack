from os.path import join, normpath

from classsettings import Settings, Config

from .base import *


class Administration(Settings):
    def DEBUG(self): return True
    def INTERNAL_IPS(self): return ('127.0.0.1',)

class Emails(Settings):
    def EMAIL_BACKEND(self):
        return 'django.core.mail.backends.console.EmailBackend'

class DATABASES(Config):
    def default(self): return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': normpath(join(DJANGO_ROOT, 'default.db')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }

class CACHES(Config):
    def default(self): return {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }

class Celery(Settings):
    def BROKER_URL(self): return 'redis://localhost:6379/0'

class Apps(Apps):
    def THIRD_PARTY_APPS(self):
        return Apps.THIRD_PARTY_APPS(self) + (
            'debug_toolbar',
        )

class Routing(Routing):
    def MIDDLEWARE_CLASSES(self):
        return Routing.MIDDLEWARE_CLASSES(self) + (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )

class DebugToolbar(Settings):
    def DEBUG_TOOLBAR_CONFIG(self): return {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TEMPLATE_CONTEXT': True,
    }
