ENV_VARS=PYTHONPATH=`pwd`
MANAGE=$(ENV_VARS) python uztrack/manage.py

run:
	$(MANAGE) runserver

syncdb:
	$(MANAGE) syncdb --noinput

shell:
	$(MANAGE) shell

migrate:
	$(MANAGE) migrate

init: syncdb migrate