from core.uzgovua.api import SmartApi
from track import queries
from track.models import TrackedWay
from .tasks import poll_history, logger


def run():
    api = SmartApi()
    tracked_ways = TrackedWay.objects.all()
    for tracked_way in tracked_ways:
        for history in queries.get_closest_histories(tracked_way):
            starting_eta = 0#poller.calc_random_eta(minutes=10)
            logger.info(u'starting poll for %s is on %s' % (history.id, starting_eta))
            poll_history.apply_async(args=(history, api), )#eta=starting_eta)

    logger.info(u'Polling service started')
