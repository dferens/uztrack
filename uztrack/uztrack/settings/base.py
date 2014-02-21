"""Common settings and globals."""
from datetime import timedelta
from sys import path
from os.path import abspath, basename, dirname, join, normpath

from .utils import settings


@settings
class Pathes(object):
    # Absolute filesystem path to the Django project directory:
    def DJANGO_ROOT(self):  return dirname(dirname(dirname(abspath(__file__))))
    # Absolute filesystem path to the top-level project folder:
    def SITE_ROOT(self): return self.DJANGO_ROOT()
    def SITE_NAME(self): return basename(self.DJANGO_ROOT())

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)

@settings
class Administration(object):
    def ADMINS(self): return (
        ('Your Name', 'your_email@example.com'),
    )
    def ALLOWED_HOSTS(self): return []
    def DEBUG(self): return False
    def MANAGERS(self): return self.ADMINS
    def SECRET_KEY(self): return "gj_(9d1j(@8bm3lm&b!0c4vkuw2(@3@(3r6d!8m1=48h7"
    def TEMPLATE_DEBUG(self): return self.DEBUG
    def WSGI_APPLICATION(self): return '%s.wsgi.application' % SITE_NAME

@settings
class Databases(object):
    def DATABASES(self): return {
        'default': {
            'ENGINE': 'django.db.backends.',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }
    def AUTH_USER_MODEL(self): return 'accounts.Profile'

@settings
class TimeLang(object):
    def TIME_ZONE(self): return 'Europe/Kiev'
    def LANGUAGE_CODE(self): return 'en-us'
    def SITE_ID(self): return 1
    def USE_I18N(self): return True
    def USE_L10N(self): return True
    def USE_TZ(self): return True

@settings
class Media(object):
    def MEDIA_ROOT(self): return normpath(join(SITE_ROOT, 'media'))
    def MEDIA_URL(self): return '/media/'

@settings
class Static(object):
    def STATIC_ROOT(self): return normpath(join(SITE_ROOT, 'assets'))
    def STATIC_URL(self): return '/static/'
    def STATICFILES_DIRS(self): return (
        normpath(join(SITE_ROOT, 'static')),
    )
    def STATICFILES_FINDERS(self): return (
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
    )

@settings
class Fixtures(object):
    def FIXTURE_DIRS(self): return (
        normpath(join(SITE_ROOT, 'fixtures')),
    )

@settings
class Templates(object):
    def TEMPLATE_CONTEXT_PROCESSORS(self): return (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.request',
    )
    def TEMPLATE_LOADERS(self): return (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
    def TEMPLATE_DIRS(self): return (
        normpath(join(SITE_ROOT, 'templates')),
    )

@settings
class Routing(object):
    def ROOT_URLCONF(self): return '%s.urls' % SITE_NAME
    def MIDDLEWARE_CLASSES(self): return (
        # Default Django middleware.
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

@settings
class Apps(object):
    def DJANGO_APPS(self): return (
        # Default Django apps:
        'django.contrib.auth',
        # django-grappelli should be installed before django.contrib.admin
        'grappelli',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Useful template tags:
        # 'django.contrib.humanize',
    )
    def THIRD_PARTY_APPS(self): return (
        'crispy_forms',
        'django_tables2',
        'rest_framework',
        'south',
    )
    def OWN_APPS(self): return (
        'accounts',
        'core',
        'poller',
        'track',
    )
    def INSTALLED_APPS(self):
        return self.DJANGO_APPS() + self.THIRD_PARTY_APPS() + self.OWN_APPS()

@settings
class CrispyForms(object):
    def CRISPY_TEMPLATE_PACK(self): return 'bootstrap3'

@settings
class OwnApps(object):
    def TICKETS_SEARCH_RANGE(self): return timedelta(days=45)

    def POLLER_WARMUP(self): return timedelta(minutes=5)

    def POLLER_CONNECTION_ERROR_RETRY(self): return timedelta(minutes=5)

@settings
class Celery(object):
    def CELERY_TIMEZONE(self): return 'Europe/Kiev'

    def CELERY_ENABLE_UTC(self): return True

@settings(to_dict=True)
class REST_FRAMEWORK(object):
    def DEFAULT_FILTER_BACKENDS(self): return (
        'rest_framework.filters.DjangoFilterBackend',
    )

@settings
class Logging(object):
    def LOGGING(self): return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    }
