from django.utils import timezone

from celery.utils.log import get_task_logger

from core.uzgovua.exceptions import ParseException
from celeryapp import app
from . import poller


logger = get_task_logger(__name__)


@app.task
def poll_history(history, api):
    execution_time = timezone.now()
    try:
        snapshot = poller.poll(history, api)
    except ParseException, e:
        logger.exception(e.message)
    else:
        next_poll_eta = poller.calc_next_eta(snapshot, history, execution_time)
        poll_history.apply_async(args=(history, api), eta=next_poll_eta)
        logger.info(u'planned next poll for %s on %s' % (history.id, next_poll_eta))
