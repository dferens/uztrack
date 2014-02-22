MANAGE=python manage.py
TEST_ENV=DJANGO_SETTINGS_MODULE="uztrack.settings.test"

cleanpyc:
	@find . -name "*.pyc" -exec rm -rf {} \;

syncdb:
	$(MANAGE) syncdb --noinput

migrate:
	$(MANAGE) migrate

test:
	$(TEST_ENV) $(MANAGE) test --pattern="test_*.py" --top-level="./"

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
