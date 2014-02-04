from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import TrackedWayDayHistory, TrackedWayDayHistorySnapshot


class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackedWayDayHistorySnapshot
        exclude = ('snapshot_data',)


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackedWayDayHistory
        fields = ('id', 'tracked_way', 'departure_date', 'places_appeared',
                  'places_disappeared', 'last_snapshot')

    last_snapshot = SnapshotSerializer('last_snapshot')


class HistoryViewSet(ModelViewSet):
    model = TrackedWayDayHistory
    filter_fields = ('tracked_way',)
    serializer_class = HistorySerializer
    # TODO: set auth
    # authentication_classes = (SessionAuthentication,)
    # permission_classes = (IsAuthenticated,)
