from django_tables2 import Table
from django_tables2 import columns
from django_tables2.utils import A

from core import columns as core_columns
from .models import Way, TrackedWay


class WayTable(Table):
    detail_url = columns.LinkColumn('way_detail', kwargs={'pk': A('id')})

    class Meta:
        model = Way
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        fields = ('id', 'station_from', 'station_to')


class TrackedWayTable(Table):
    class Meta:
        model = TrackedWay
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        exclude = ('id',)

    way = columns.LinkColumn('way_detail', kwargs={'pk': A('way.pk')})
    days = columns.TemplateColumn(template_name='blocks/bitfield.html')
    detail = core_columns.FixedLinkColumn('track_detail', kwargs={'pk': A('pk')}, text='See tickets')