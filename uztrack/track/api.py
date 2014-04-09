from datetime import time

from django.utils import timezone

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
        dep_min_time = tracked_way.dep_min_time
        dep_min_time = time(0, 0) if dep_min_time is None else dep_min_time

        args = (way.station_id_from, way.station_id_to,
                history.departure_date, dep_min_time)
        route_trains = super(Api, self).get_stations_routes(*args)

        def filter_func(train):
            if tracked_way.dep_max_time is not None:
                if train.station_from.date.time() > tracked_way.dep_max_time:
                    return False

            if tracked_way.arr_min_time is not None:
                if train.station_till.date.time() < tracked_way.arr_min_time:
                    return False

            if tracked_way.arr_max_time is not None:
                if train.station_till.date.time() > tracked_way.arr_max_time:
                    return False

            return True

        route_trains.trains = filter(filter_func, route_trains.trains)
        return route_trains

