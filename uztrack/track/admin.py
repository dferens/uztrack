from django.contrib import admin

from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from bitfield.admin import BitFieldListFilter

from . import models


class WayAdmin(admin.ModelAdmin):
    list_display = ('station_from', 'station_to')
    list_filter = ('station_from', 'station_to')


class TrackedWayAdmin(admin.ModelAdmin):
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }
    list_filter = (
        ('days', BitFieldListFilter),
    )
    list_display = ('way', 'owner', 'days_list', 'departure_time', 'arrival_time')

    def _render_time(self, value):
        return value.strftime('%H:%M') if value else '...'

    def departure_time(self, obj):
        min = self._render_time(obj.dep_min_time)
        max = self._render_time(obj.dep_max_time)
        return '%s - %s' % (min, max)

    def arrival_time(self, obj):
        min = self._render_time(obj.arr_min_time)
        max = self._render_time(obj.arr_max_time)
        return '%s - %s' % (min, max)

    def days_list(self, obj):
        return  ','.join(obj.selected_weekdays)

    departure_time.short_description = 'Departure time'
    departure_time.admin_order_field = 'dep_min_time'
    arrival_time.short_description = 'Arrival time'
    arrival_time.admin_order_field = 'arr_min_time'
    days_list.short_description = 'Days'


class HistoryAdmin(admin.ModelAdmin):
    ordering = ('tracked_way__way__id', 'tracked_way__days',
                'tracked_way__dep_min_time', 'departure_date')
    list_display = ('way', 'weekdays', 'active', 'dep_min_time', 'departure_date')

    def way(self, obj):
        return obj.tracked_way.way

    def weekdays(self, obj):
        return ', '.join(obj.tracked_way.selected_weekdays)

    def dep_min_time(self, obj):
        return obj.tracked_way.dep_min_time


class SnapshotAdmin(admin.ModelAdmin):
    ordering = ('history', '-made_on',)
    list_display = ('history', 'made_on')


admin.site.register(models.Way, WayAdmin)
admin.site.register(models.TrackedWay, TrackedWayAdmin)
admin.site.register(models.TrackedWayDayHistory, HistoryAdmin)
admin.site.register(models.TrackedWayDayHistorySnapshot, SnapshotAdmin)
