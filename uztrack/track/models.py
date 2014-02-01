import datetime
import operator
from dateutil import rrule

from django.db import models
from django.dispatch import Signal
from django.contrib import admin
from django.core.urlresolvers import reverse

from bitfield import BitField
from jsonfield import JSONField

from . import utils


class Way(models.Model):
    """
    Defines abstract directed way between two train stations.
    """
    class Meta:
        unique_together = (('station_from_id', 'station_till_id'))

    station_from = models.CharField(max_length=30)
    station_till = models.CharField(max_length=30)
    station_from_id = models.IntegerField()
    station_till_id = models.IntegerField()

    def __unicode__(self):
        return u'%s - %s' % (self.station_from, self.station_till)


class TrackedWay(models.Model):
    """
    Says that particular way should be checked for tickets on given departure weekdays.
    """
    way = models.ForeignKey(Way)
    days = BitField(flags=utils.WEEKDAYS)
    start_time = models.TimeField(default=lambda: datetime.time(0, 0))

    def next_dates(self, till):
        """
        Returns list of next arrival dates, starting from now.

        :param till: :class:`datetime.date` object, specified upper limit
        :return: list of :class:`datetime.date` objects
        """
        starts_from = datetime.datetime.now()
        dateutil_weekdays = map(utils.get_dateutil_weekday, self.selected_weekdays)
        rule = rrule.rrule(rrule.WEEKLY, byweekday=dateutil_weekdays, until=till)
        dates = [x.date() for x in rule]
        if starts_from in dates:
            dates.remove(starts_from.date())
        return dates

    @property
    def selected_weekdays(self):
        """
        Returns days it should check tickets on.

        :return: generator of weekday names, like ('Monday', 'Friday', ...)
        """
        return (wday for wday, is_set in self.days if is_set)


class TrackedWayDayHistory(models.Model):
    """
    Describes tickets history for a given :class:`TrackedWay` way for a given day

    Field ``places_appeared`` points to :class:`TrackedWayDayHistorySnapshot`
    snapshot, when tickets were been found for the first time.
    Field ``places_disappeared`` points to :class:`TrackedWayDayHistorySnapshot`
    snapshot, when tickets were not been found for the first time.
    """
    class Meta:
        unique_together = (('tracked_way', 'departure_date'))

    tracked_way = models.ForeignKey(TrackedWay, related_name='histories')
    departure_date = models.DateField()
    places_appeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                            related_name='marks_appear', null=True)
    places_disappeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                               related_name='marks_disappear', null=True)

    on_places_appeared = Signal()
    on_places_disappeared = Signal()

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
        ordering = ['made_on']
        get_latest_by = 'made_on'

    history = models.ForeignKey(TrackedWayDayHistory, related_name='snapshots')
    made_on = models.DateTimeField(auto_now_add=True)
    total_places_count = models.IntegerField()
    snapshot_data = JSONField()

    def save(self, *args, **kwargs):
        super(TrackedWayDayHistorySnapshot, self).save(*args, **kwargs)
        self.history.check_snapshot(self)