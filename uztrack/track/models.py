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
    class Meta:
        unique_together = (('station_from_id', 'station_till_id'))

    station_from = models.CharField(max_length=30)
    station_till = models.CharField(max_length=30)
    station_from_id = models.IntegerField()
    station_till_id = models.IntegerField()

    def __unicode__(self):
        return u'%s - %s' % (self.station_from, self.station_till)

    @property
    def detail_url(self):
        return 'Edit details'


class TrackedWay(models.Model):
    way = models.ForeignKey(Way)
    days = BitField(flags=utils.WEEKDAYS)
    start_time = models.TimeField(default=lambda: datetime.time(0, 0))

    def next_dates(self, till, starts_from=None):
        if starts_from is None:
            starts_from = datetime.date.today()

        dateutil_weekdays = map(utils.get_dateutil_weekday, self.selected_days)
        rule = rrule.rrule(rrule.WEEKLY, byweekday=dateutil_weekdays, until=till)
        dates = [x.date() for x in rule]

        if starts_from in dates:
            dates.remove(starts_from.date())
        return dates

    @property
    def selected_days(self):
        return (wday for wday, is_set in self.days if is_set)

    @property
    def detail_url(self):
        return 'Edit details'


class TrackedWayDayHistory(models.Model):
    class Meta:
        unique_together = (('tracked_way', 'departure_date'))

    tracked_way = models.ForeignKey(TrackedWay, related_name='histories')
    departure_date = models.DateField()
    places_appeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                            related_name='marks_appear',
                                            null=True)
    places_disappeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                               related_name='marks_disappear',
                                               null=True)

    on_places_appeared = Signal()
    on_places_dissapeared = Signal()

    @property
    def last_snapshot(self):
        return self.snapshots[-1]

    def check_snapshot(self, snapshot):
        if self.places_appeared is None:
            if snapshot.total_places_count > 0:
                self.places_appeared = snapshot
                self.save()
                self.on_places_appeared.send(sender=self)

        elif self.places_disappeared is None:
            if snapshot.total_places_count == 0:
                self.places_disappeared = snapshot
                self.save()
                self.on_places_dissapeared.send(sender=self)
        else:
            # Regular snapshot
            pass


class TrackedWayDayHistorySnapshot(models.Model):
    class Meta:
        ordering = ['made_on']

    history = models.ForeignKey(TrackedWayDayHistory, related_name='snapshots')
    made_on = models.DateTimeField(auto_now_add=True)
    total_places_count = models.IntegerField()
    snapshot_data = JSONField()

    def save(self, *args, **kwargs):
        val = super(TrackedWayDayHistorySnapshot, self).save(*args, **kwargs)
        self.history.check_snapshot(self)