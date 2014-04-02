#!/usr/bin/env python
from __future__ import absolute_import

import os
from django.conf import settings
from celery import Celery
from celery.signals import celeryd_init

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uztrack.settings.production")

app = Celery(settings.SITE_NAME)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if __name__ == '__main__':
    app.start()
