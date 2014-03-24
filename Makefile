HONCHO=honcho run
TEST_HONCHO=honcho -e .env.test run
MANAGE=$(HONCHO) uztrack/manage.py
TEST_CMD=uztrack/manage.py test --pattern="test_*.py" --top-level-dir="uztrack/" uztrack

cleanpyc:
	@find . -name "*.pyc" -exec rm -rf {} \;

syncdb:
	$(MANAGE) syncdb --noinput

migrate:
	$(MANAGE) migrate

test:
	$(TEST_HONCHO) $(TEST_CMD)

testcover:
	$(TEST_HONCHO) coverage run $(TEST_CMD)
	coverage report

collectstatic:
	$(MANAGE) collectstatic --noinput

shell:
	$(MANAGE) shell

init: syncdb migrate test
