import django_tables2 as tables

from core.tables import DetailLinkTable
from .models import Way, TrackedWay


class WayTable(tables.Table):
    detail_url = tables.LinkColumn('way_detail', kwargs={'pk': tables.A('pk')})

    class Meta:
        model = Way
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        fields = ('id', 'station_from', 'station_till', 'detail_url')


class TrackedWayTable(tables.Table):
    way = tables.LinkColumn('way_detail', kwargs={'pk': tables.A('pk')})
    days = tables.TemplateColumn(template_name='blocks/bitfield.html')
    detail_url = tables.LinkColumn('track_detail', kwargs={'pk': tables.A('pk')})

    class Meta:
        model = TrackedWay
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        fields = ('id', 'way', 'days', 'start_time', 'detail_url')
