from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import TrackedWayDayHistory


class HistoryViewSet(ModelViewSet):
    model = TrackedWayDayHistory
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
