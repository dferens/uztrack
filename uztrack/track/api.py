from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.uzgovua.api import SmartApi
from . import models


class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TrackedWayDayHistorySnapshot
        exclude = ('snapshot_data',)


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TrackedWayDayHistory
        fields = ('id', 'tracked_way', 'departure_date', 'places_appeared',
                  'places_disappeared', 'last_snapshot')

    last_snapshot = SnapshotSerializer('last_snapshot')


class HistoryViewSet(ModelViewSet):
    model = models.TrackedWayDayHistory
    filter_fields = ('tracked_way',)
    serializer_class = HistorySerializer
    # TODO: set auth
    # authentication_classes = (SessionAuthentication,)
    # permission_classes = (IsAuthenticated,)


class SnapshotViewSet(ModelViewSet):
    model = models.TrackedWayDayHistorySnapshot
    filter_fields = ('history',)
    serializer_class = SnapshotSerializer


class Api(SmartApi):

    def get_stations_routes(self, history):
        way = history.tracked_way.way
        tracked_way = history.tracked_way
        args = (way.station_id_from, way.station_id_to,
                history.departure_date, tracked_way.start_time)
        return super(Api, self).get_stations_routes(*args)
