from django.db import models


class Way(models.Model):
    class Meta:
        unique_together = (('station_from_id', 'station_till_id'))

    station_from = models.CharField(max_length=30)
    station_till = models.CharField(max_length=30)
    station_from_id = models.IntegerField()
    station_till_id = models.IntegerField()