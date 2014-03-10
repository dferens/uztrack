MANAGE=uztrack/manage.py
TEST_CMD=$(MANAGE) test --pattern="test_*.py" --top-level-dir="uztrack/" uztrack
TEST_ENV=DJANGO_SETTINGS_MODULE="uztrack.settings.test"

cleanpyc:
	@find . -name "*.pyc" -exec rm -rf {} \;

syncdb:
	$(MANAGE) syncdb --noinput

migrate:
	$(MANAGE) migrate

test:
	$(TEST_ENV) $(TEST_CMD)

testcover:
	$(TEST_ENV) coverage run $(TEST_CMD)
	coverage report

collectstatic:
	$(MANAGE) collectstatic --noinput

run:
	$(MANAGE) runserver

celery:
	DJANGO_SETTINGS_MODULE="uztrack.settings.local" python celeryapp.py worker -l info

shell:
	$(MANAGE) shell

init: syncdb migrate test
