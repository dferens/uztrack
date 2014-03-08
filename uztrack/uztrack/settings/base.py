"""Common settings and globals."""
from datetime import timedelta
from sys import path
from os.path import abspath, basename, dirname, join, normpath

from classsettings import Settings, Config, from_env


class Pathes(Settings):
    # Absolute filesystem path to the Django project directory:
    def DJANGO_ROOT(self):  return dirname(dirname(dirname(abspath(__file__))))
    # Absolute filesystem path to the top-level project folder:
    def SITE_ROOT(self): return dirname(self.DJANGO_ROOT())
    def SITE_NAME(self): return basename(self.DJANGO_ROOT())

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)

class Administration(Settings):
    def ADMINS(self): return (
        ('Your Name', 'your_email@example.com'),
    )
    def ALLOWED_HOSTS(self): return []
    def DEBUG(self): return False
    def MANAGERS(self): return self.ADMINS()
    def SECRET_KEY(self): return "gj_(9d1j(@8bm3lm&b!0c4vkuw2(@3@(3r6d!8m1=48h7"
    def TEMPLATE_DEBUG(self): return self.DEBUG()
    def WSGI_APPLICATION(self): return '%s.wsgi.application' % SITE_NAME

class Databases(Settings):
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

class TimeLang(Settings):
    def TIME_ZONE(self): return 'Europe/Kiev'
    def LANGUAGE_CODE(self): return 'en-us'
    def SITE_ID(self): return 1
    def USE_I18N(self): return True
    def USE_L10N(self): return True
    def USE_TZ(self): return True

class Media(Settings):
    def MEDIA_ROOT(self): return normpath(join(SITE_ROOT, 'media'))
    def MEDIA_URL(self): return '/media/'

class Static(Settings):
    def STATIC_ROOT(self): return normpath(join(SITE_ROOT, 'assets'))
    def STATIC_URL(self): return '/static/'
    def STATICFILES_DIRS(self): return (
        normpath(join(DJANGO_ROOT, 'static')),
    )
    def STATICFILES_FINDERS(self): return (
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
    )

class Fixtures(Settings):
    def FIXTURE_DIRS(self): return (
        normpath(join(DJANGO_ROOT, 'fixtures')),
    )

class Templates(Settings):
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
        normpath(join(DJANGO_ROOT, 'templates')),
    )

class Routing(Settings):
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

class Apps(Settings):
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

class CrispyForms(Settings):
    def CRISPY_TEMPLATE_PACK(self): return 'bootstrap3'

class OwnApps(Settings):
    def TICKETS_SEARCH_RANGE(self): return timedelta(days=45)
    def POLLER_DRY_RUN(self): return False
    def POLLER_WARMUP(self): return timedelta(minutes=5)
    def POLLER_AUTOSTART(self): return True
    def POLLER_AUTOSTART_NEW(self): return True
    def POLLER_CONNECTION_ERROR_RETRY(self): return timedelta(minutes=5)

class Celery(Settings):
    def CELERY_TIMEZONE(self): return 'Europe/Kiev'
    def CELERY_ENABLE_UTC(self): return True

class REST_FRAMEWORK(Config):
    def DEFAULT_FILTER_BACKENDS(self): return (
        'rest_framework.filters.DjangoFilterBackend',
    )

class Logging(Settings):
    def LOGGING(self): return {
        'version': 1,
        'disable_existing_loggers': True,
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
                'formatter': 'verbose'
            },
            'celery': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'celery.log',
                'formatter': 'simple',
                'maxBytes': 1024 * 1024 * 100,  # 100 mb
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            'poller.poller': {
                'handlers': ['console', 'mail_admins'],
                'level': 'INFO',
            },
            'celery': {
                'handlers': ['celery'],
                'level': 'INFO',
            },
        }
    }
