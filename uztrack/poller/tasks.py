from celery.decorators import task
from celery.utils.log import get_task_logger

from django.utils import timezone

from core.uzgovua.api import SmartApi
from core.uzgovua.exceptions import ParseException
from track import queries
from track.models import TrackedWay

from . import poller


logger = get_task_logger(__name__)


@task
def start_polling_service():
    logger.info(u'Started polling service')
    api = SmartApi()
    for tracked_way in TrackedWay.objects.all():
        for history in queries.get_closest_histories(tracked_way):
            starting_eta = poller.calc_random_eta(minutes=10)
            logger.info(u'starting poll for %s is on %s' % (history, starting_eta))
            poll_history.apply_async(args=(history, api), eta=starting_eta)


@task
def poll_history(history, api):
    execution_time = timezone.now()
    try:
        snapshot = poller.poll(history, api)
    except ParseException, e:
        logger.exception(e.message)
        print e.message
    else:
        next_poll_eta = poller.calc_next_eta(snapshot, history, execution_time)
        poll_history.apply_async(args=(history, api), eta=next_poll_eta)
        logger.info(u'next poll for %s is on %s' % (history, next_poll_eta))
