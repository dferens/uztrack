=======
uztrack
=======


Features
========
- tracks status of specific tickets at booking.uz.gov.ua and sends emails;


Installation of Dependencies
=============================

Depending on where you are installing dependencies:

In development::

    $ pip install -r requirements/local.txt

For production::

    $ pip install -r requirements.txt

Install static with bower::

    $ make bowerinstall

Running
=======

You can use foreman/honcho to run it locally::

    $ cp .env.default .env
    $ ln -s Procfile.dev Procfile
    $ make run

Production notes
================

Redis used as celery broker has some `problems <http://docs.celeryproject.org/en/latest/getting-started/brokers/redis.html#caveats>`_ with ETA tasks, use rabbitmq instead.
