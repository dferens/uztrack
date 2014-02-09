MANAGE=python uztrack/manage.py
CELERY=python uztrack/celeryapp.py
TEST_ENV=DJANGO_SETTINGS_MODULE="uztrack.settings.test"
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
	$(TEST_ENV) $(MANAGE) test --pattern="test_*.py" $(APPS)

migrate:
	$(MANAGE) migrate

init: syncdb migrate test
