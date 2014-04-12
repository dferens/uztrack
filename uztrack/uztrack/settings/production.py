import dj_database_url
from classsettings import Settings, Config, from_env

from .base import *


class Administration(Settings):
    def ALLOWED_HOSTS(self): return ['.swinemaker.org']
    @from_env
    def SECRET_KEY(self): pass

class Emails(Settings):
    def EMAIL_BACKEND(self): return 'django.core.mail.backends.smtp.EmailBackend'
    @from_env
    def EMAIL_HOST(self): pass
    @from_env
    def EMAIL_HOST_PASSWORD(self): pass
    @from_env
    def EMAIL_HOST_USER(self): pass
    @from_env
    def EMAIL_PORT(self): return 587
    def EMAIL_SUBJECT_PREFIX(self): return '[%s] ' % SITE_NAME
    def EMAIL_USE_TLS(self): return True
    def SERVER_EMAIL(self): return self.EMAIL_HOST_USER()

class DATABASES(Config):
    @from_env(key='DATABASE_URL', through=dj_database_url.parse)
    def default(self): pass

class Celery(Settings):    
    @from_env
    def BROKER_URL(self): pass
