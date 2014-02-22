from django.conf import settings
from django.utils import timezone

from celery.utils.log import get_task_logger
from requests.exceptions import ConnectionError

from core.uzgovua.exceptions import ParseException
from celeryapp import app
from track.models import TrackedWayDayHistory as History
from . import poller


logger = get_task_logger(__name__)


@app.task
def poll_history(history_id, api, stop_on):
    """
    Polls given :class:`track.models.TrackedWayDayHistory` history with given api
    instance.
    Makes api call, saves results, plans next poll.
    """
    history = History.objects.get(id=history_id)
    execution_time = timezone.now()
    try:
        snapshot = poller.poll(history, api)
    except ConnectionError, e:
        logger.error('Connection error')
        next_poll_eta = execution_time + settings.POLLER_CONNECTION_ERROR_RETRY
        logger.info(u'planned next poll for %s on %s' % (history_id, next_poll_eta))
    except Exception, e:
        logger.exception(e)
    else:
        next_poll_eta = poller.calc_next_eta(snapshot, history)

        if next_poll_eta < stop_on:
            poll_history.apply_async(args=(history_id, api, stop_on), eta=next_poll_eta)
            logger.info(u'planned next poll for %s on %s' % (history_id, next_poll_eta))
        else:
            logger.info(u'stopped poll service for %s' % (history_id))
