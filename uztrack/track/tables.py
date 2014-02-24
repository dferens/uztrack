from django_tables2 import Table
from django_tables2 import columns
from django_tables2.utils import A

from core import columns as core_columns
from .models import Way, TrackedWay, TrackedWayDayHistorySnapshot as Snapshot


class WayTable(Table):
    class Meta:
        model = Way
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        fields = ('id', 'station_from', 'station_to')

    detail_url = columns.LinkColumn('way-detail', kwargs={'pk': A('id')})



class TrackedWayTable(Table):
    class Meta:
        model = TrackedWay
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        exclude = ('id',)

    way = columns.LinkColumn('way-detail', kwargs={'pk': A('way.pk')})
    days = columns.TemplateColumn(template_name='blocks/bitfield.html')
    detail = core_columns.FixedLinkColumn('trackedway-detail', kwargs={'pk': A('pk')}, text='See tickets')
