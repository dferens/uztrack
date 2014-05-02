"""Common settings and globals."""
from datetime import timedelta
from sys import path
from os.path import abspath, basename, dirname, join, normpath

from celery.schedules import crontab
from classsettings import Settings, Config, from_env


class Pathes(Settings):
    # Absolute filesystem path to the Django project directory:
    DJANGO_ROOT = dirname(dirname(dirname(abspath(__file__))))
    # Absolute filesystem path to the top-level project folder:
    SITE_ROOT = dirname(DJANGO_ROOT)
    SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)

class Administration(Settings):    
    def ALLOWED_HOSTS(self): return []
    def DEBUG(self): return False
    def PROFILE(selF): return False
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
    def STATIC_ROOT(self): return normpath(join(SITE_ROOT, 'static'))
    def STATIC_URL(self): return '/static/'
    def STATICFILES_DIRS(self): return (
        normpath(join(DJANGO_ROOT, 'static')),
    )
    def STATICFILES_FINDERS(self): return (
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'djangobower.finders.BowerFinder',
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

        'core.context_processors.site_name',
    )
    def TEMPLATE_LOADERS(self): return (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
    def TEMPLATE_DIRS(self): return (
        normpath(join(DJANGO_ROOT, 'templates')),
    )

class Routing(Settings):
    def LOGIN_URL(self): return '/admin/'
    def ROOT_URLCONF(self): return '%s.urls' % SITE_NAME
    def MIDDLEWARE_CLASSES(self): 
        # Default Django middleware.
        base = ('django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware')
        base += ('profiler.middleware.ProfilerMiddleware',) if PROFILE else ()
        return base

class Apps(Settings):
    def DJANGO_APPS(self): return (
        # Default Django apps:
        'django.contrib.auth',
        # django-grappelli should be installed before django.contrib.admin
        'grappelli',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.humanize',
        'django.contrib.messages',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.staticfiles',
    )
    def THIRD_PARTY_APPS(self): 
        base = ('profiler',
                'crispy_forms',
                'djangobower',
                'django_tables2',
                'rest_framework',
                'south')
        base +=  ('profiler',) if PROFILE else ()
        return base

    def OWN_APPS(self): return (
        'accounts',
        'core',
        'poller',
        'track',
    )
    def INSTALLED_APPS(self):
        return self.DJANGO_APPS() + self.THIRD_PARTY_APPS() + self.OWN_APPS()

class Bower(Settings):
    def BOWER_COMPONENTS_ROOT(self): return SITE_ROOT
    def BOWER_INSTALLED_APPS(self): return (
        'angular',
        'angular-bootstrap',
        'angular-ui-select2',
        'angular-rangeslider',
        'bootstrap#3',
        'bootstrap-sortable',
        'bootstrap-switch',
        'cal-heatmap',
        'eonasdan-bootstrap-datetimepicker',
        'jquery',
        'select2-bootstrap-css',
        'underscore',
    )

class CrispyForms(Settings):
    def CRISPY_TEMPLATE_PACK(self): return 'bootstrap3'

class OwnApps(Settings):
    def TICKETS_SEARCH_RANGE(self): return timedelta(days=45)
    def POLLER_DRY_RUN(self): return False
    def POLLER_WARMUP(self): return timedelta(minutes=5)
    def POLLER_AUTOSTART(self): return True
    def POLLER_AUTOSTART_NEW(self): return True
    def POLLER_INTERVAL(self): return timedelta(hours=1)
    def POLLER_CONNECTION_ERROR_RETRY(self): return timedelta(minutes=5)
    def POLLER_WAIT_FOR_CELERY(self): return False

class Celery(Settings):
    CELERY_SEND_TASK_ERROR_EMAILS = True
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_ENABLE_UTC = True
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Europe/Kiev'
    CELERYBEAT_SCHEDULE = {
        'midnight-synchronise': {
            'task': 'poller.tasks.synchronize',
            'schedule': crontab(minute=0, hour=0),
        },
    }

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
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            'poller': {
                'handlers': ['console', 'mail_admins'],
                'level': 'INFO',
            },
            'core.uzgovua': {
                'handlers': ['console', 'mail_admins'],
                'level': 'INFO'
            }
        }
    }
