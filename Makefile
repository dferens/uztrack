ENV_VARS=PYTHONPATH=`pwd`
MANAGE=$(ENV_VARS) python uztrack/manage.py

run:
	$(MANAGE) runserver

syncdb:
	$(MANAGE) syncdb --noinput

migrate:
	$(MANAGE) migrate