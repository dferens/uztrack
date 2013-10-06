import datetime
import operator
from dateutil import rrule

from django.db import models
from django.contrib import admin

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


class TrackedWay(models.Model):
    class Meta:
        unique_together = (('way', 'days', 'start_time'))

    way = models.ForeignKey(Way)
    days = BitField(flags=utils.WEEKDAYS)
    start_time = models.TimeField(default=lambda: datetime.time(0, 0))

    def next_dates(self, till, starts_from=None):
        if starts_from is None:
            starts_from = datetime.date.today()

        weekdays = [wday for wday, is_set in self.days if is_set]
        dateutil_weekdays = map(utils.get_dateutil_weekday, weekdays)
        rule = rrule.rrule(rrule.WEEKLY, byweekday=dateutil_weekdays, until=till)
        dates = [x.date() for x in rule]

        if starts_from.date() in dates:
            dates.remove(starts_from.date())
        return dates


class TrackedWayDayHistory(models.Model):
    tracked_way = models.ForeignKey(TrackedWay)
    arrival_date = models.DateField()
    places_appeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                            related_name='marks_appear',
                                            null=True)
    places_disappeared = models.OneToOneField('track.TrackedWayDayHistorySnapshot',
                                               related_name='marks_disappear')


class TrackedWayDayHistorySnapshot(models.Model):
    history = models.ForeignKey(TrackedWayDayHistory, related_name='snapshots')
    made_on = models.DateTimeField(auto_now_add=True)
    total_places_count = models.IntegerField()
    snapshot_data = JSONField()