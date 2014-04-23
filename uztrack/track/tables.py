from django_tables2 import Table
from django_tables2 import columns
from django_tables2.utils import A

from core.columns import FixedLinkColumn
from .models import Way, TrackedWay, TrackedWayDayHistorySnapshot as Snapshot


class WayTable(Table):
    class Meta:
        model = Way
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        fields = ('id', 'station_from', 'station_to')

    detail_url = FixedLinkColumn('way-detail', kwargs={'pk': A('pk')}, text='Details')



class TrackedWayTable(Table):
    class Meta:
        model = TrackedWay
        attrs = {'class': 'table table-striped table-bordered table-hover'}
        fields = ('way', 'days', 'departure_time', 'arrival_time', 'detail')

    way = columns.LinkColumn('way-detail', kwargs={'pk': A('way.pk')})
    detail = FixedLinkColumn('trackedway-detail', kwargs={'pk': A('pk')}, text='See tickets')
    departure_time = columns.Column(accessor=A('id'),
                                    verbose_name=u'departure time')
    arrival_time = columns.Column(accessor=A('id'),
                                  verbose_name=u'arrival time')

    def __render_time(self, value):
        return value.strftime('%H:%M') if value else '...'

    def render_days(self, value, bound_row=None, **kwargs):
        tracked_way = bound_row.record

        if tracked_way.is_repeated:
            return ', '.join(k for (k, v) in tracked_way.days.iteritems() if v)
        else:
            return tracked_way.departure_date

    def render_departure_time(self, value, bound_row=None, **kwargs):
        tracked_way = bound_row.record
        min = self.__render_time(tracked_way.dep_min_time)
        max = self.__render_time(tracked_way.dep_max_time)
        return '%s - %s' % (min, max)

    def render_arrival_time(self, value, bound_row=None, **kwargs):
        tracked_way = bound_row.record
        min = self.__render_time(tracked_way.arr_min_time)
        max = self.__render_time(tracked_way.arr_max_time)
        return '%s - %s' % (min, max)        
