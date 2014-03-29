import operator
from dateutil import rrule
from datetime import time

from django.db import models
from django.dispatch import Signal
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import timezone

from bitfield import BitField
from jsonfield import JSONField

from . import utils


class Way(models.Model):
    """
    Defines abstract directed way between two train stations.
    """
    class Meta:
        unique_together = (('station_id_from', 'station_id_to'))

    station_id_from = models.IntegerField()
    station_from = models.CharField(max_length=30)
    station_id_to = models.IntegerField()
    station_to = models.CharField(max_length=30)

    def __unicode__(self):
        return u'%s - %s' % (self.station_from, self.station_to)


class TrackedWay(models.Model):
    """
    Says that particular way should be checked for tickets on given departure weekdays.
    """
    way = models.ForeignKey(Way)
    days = BitField(flags=utils.WEEKDAYS)
    start_time = models.TimeField(default=time(0, 0))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        days = ', '.join(self.selected_weekdays)
        return '%s-%s on %s' % (self.way.station_from, self.way.station_to,
                                ', '.join(self.selected_weekdays))

    def next_dates(self, till):
        """
        Returns list of next arrival dates, starting from now.

        :param till: :class:`datetime.date` object, specified upper limit
        :return: list of :class:`datetime.date` objects
        """
        starts_from = timezone.now()
        dateutil_weekdays = map(utils.get_dateutil_weekday, self.selected_weekdays)
        rule = rrule.rrule(rrule.WEEKLY, byweekday=dateutil_weekdays, until=till)
        return [x.date() for x in rule]

    @property
    def selected_weekdays(self):
        """
        Returns days it should check tickets on.

        :return: generator of weekday names, like ('Monday', 'Friday', ...)
        """
        return (wday for wday, is_set in self.days if is_set)

    def save(self, *args, **kwargs):
        import poller.queries
        
        created = self.pk is None
        super(TrackedWay, self).save(*args, **kwargs)
        if created: poller.queries.poll_tracked_way(self)


class TrackedWayDayHistory(models.Model):
    """
    Describes tickets history for a given :class:`TrackedWay` way for a given day

    Field ``places_appeared`` points to :class:`TrackedWayDayHistorySnapshot`
    snapshot, when tickets were been found for the first time.
    Field ``places_disappeared`` points to :class:`TrackedWayDayHistorySnapshot`
    snapshot, when tickets were not been found for the first time.
    """
    class Meta:
        verbose_name = u'tracked way history'
        verbose_name_plural = u'tracked way histories'
        unique_together = (('tracked_way', 'departure_date'))

    tracked_way = models.ForeignKey(TrackedWay, related_name='histories')
    departure_date = models.DateField()
    places_appeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                            related_name='marks_appear', null=True)
    places_disappeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                               related_name='marks_disappear', null=True)

    on_places_appeared = Signal()
    on_places_disappeared = Signal()

    def __unicode__(self):
        return u'%s on %s' % (self.tracked_way, self.departure_date)

    @property
    def last_snapshot(self):
        return self.snapshots.latest()

    def check_snapshot(self, snapshot):
        """
        Checks that places for current way history were appeared or disappeared
        within given snapshot.
        """
        if self.places_appeared is None:
            if snapshot.total_places_count > 0:
                self.places_appeared = snapshot
                self.save()
                self.on_places_appeared.send(sender=self)

        elif self.places_disappeared is None:
            if snapshot.total_places_count == 0:
                self.places_disappeared = snapshot
                self.save()
                self.on_places_disappeared.send(sender=self)
        else:
            # Regular snapshot
            pass


class TrackedWayDayHistorySnapshot(models.Model):
    """
    Tickets history snapshot.
    """
    class Meta:
        verbose_name = u'history snapshot'
        verbose_name_plural = u'history snapshots'
        get_latest_by = 'made_on'

    history = models.ForeignKey(TrackedWayDayHistory, related_name='snapshots')
    made_on = models.DateTimeField(auto_now_add=True)
    total_places_count = models.IntegerField()
    snapshot_data = JSONField()

    def save(self, *args, **kwargs):
        super(TrackedWayDayHistorySnapshot, self).save(*args, **kwargs)
        self.history.check_snapshot(self)
