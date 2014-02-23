MANAGE=python manage.py
TEST_ENV=DJANGO_SETTINGS_MODULE="uztrack.settings.test"
TEST_CMD=manage.py test --pattern="test_*.py" --top-level="./"

cleanpyc:
	@find . -name "*.pyc" -exec rm -rf {} \;

syncdb:
	$(MANAGE) syncdb --noinput

migrate:
	$(MANAGE) migrate

test:
	$(TEST_ENV) python $(TEST_CMD)

testcover:
	$(TEST_ENV) coverage run $(TEST_CMD)
	coverage report

collectstatic:
	rm -rf assets/
	$(MANAGE) collectstatic --noinput

run:
	$(MANAGE) runserver

celery:
	DJANGO_SETTINGS_MODULE="uztrack.settings.local" python celeryapp.py worker -l info

shell:
	$(MANAGE) shell

init: syncdb migrate test
