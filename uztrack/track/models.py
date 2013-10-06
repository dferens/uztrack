from django.db import models
from django.contrib import admin

from bitfield import BitField


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