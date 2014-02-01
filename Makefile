MANAGE=python uztrack/manage.py
TEST_ENV=DJANGO_SETTINGS_MODULE="uztrack.settings.test"

run:
	$(MANAGE) runserver

syncdb:
	$(MANAGE) syncdb --noinput

shell:
	$(MANAGE) shell

test:
	$(TEST_ENV) $(MANAGE) test --pattern="test_*.py" track

migrate:
	$(MANAGE) migrate

init: syncdb migrate test