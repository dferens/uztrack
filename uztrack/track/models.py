import datetime

from django.db import models
from django.contrib import admin

from bitfield import BitField
from jsonfield import JSONField


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
    days = BitField(flags=(
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ))
    start_time = models.TimeField(default=lambda: datetime.time(0, 0))


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