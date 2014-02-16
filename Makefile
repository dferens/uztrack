LOCAL_ENV=DJANGO_SETTINGS_MODULE="uztrack.settings.local"
TEST_ENV=DJANGO_SETTINGS_MODULE="uztrack.settings.test"
MANAGE=$(LOCAL_ENV) python uztrack/manage.py
CELERY=$(LOCAL_ENV) python uztrack/celeryapp.py
APPS=accounts core poller track

collectstatic:
	$(MANAGE) collectstatic --noinput

run:
	$(MANAGE) runserver

celery:
	$(CELERY) worker -l info

cleanpyc:
	@find . -name "*.pyc" -exec rm -rf {} \;

syncdb:
	$(MANAGE) syncdb --noinput

shell:
	$(MANAGE) shell

test:
	$(MANAGE) $(TEST_ENV) test --pattern="test_*.py" $(APPS)

migrate:
	$(MANAGE) migrate

init: syncdb migrate test
