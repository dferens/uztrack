from django.utils import timezone

from celery.utils.log import get_task_logger

from core.uzgovua.exceptions import ParseException
from celeryapp import app
from . import poller


logger = get_task_logger(__name__)


@app.task
def poll_history(history, api, stop_on):
    """
    Polls given :class:`track.models.TrackedWayDayHistory` history with given api
    instance.
    Makes api call, saves results, plans next poll.
    """
    execution_time = timezone.now()
    try:
        snapshot = poller.poll(history, api)
    except Exception, e:
        logger.exception(e.message)
    else:
        next_poll_eta = poller.calc_next_eta(snapshot, history, execution_time)

        if next_poll_eta < stop_on:
            poll_history.apply_async(args=(history, api, stop_on), eta=next_poll_eta)
            logger.info(u'planned next poll for %s on %s' % (history.id, next_poll_eta))
        else:
            logger.info(u'stopped poll service for %s' % (history.id))
