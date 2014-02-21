import dj_database_url

from .base import *
from .utils import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


@settings
class Administration(object):
    def ALLOWED_HOSTS(self): return []
    @from_env
    def SECRET_KEY(self): pass

@settings
class Emails(object):
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

@settings(to_dict=True)
class DATABASES(object):
    def default(self): dj_database_url.parse(get_env_setting('DATABASE_URL')),

@settings
class Celery(object):
    def CELERY_TASK_SERIALIZER(self): return 'json'
    def CELERY_ACCEPT_CONTENT(self): return ['json']
    @from_env
    def BROKER_URL(self): pass
