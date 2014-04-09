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
    list_display = ('way', 'owner', 'days_list', 'dep_min_time_24h')

    def dep_min_time_24h(self, obj):
        return obj.dep_min_time.strftime('%H:%M') if obj.dep_min_time else ''
    dep_min_time_24h.short_description = 'Start time'

    def days_list(self, obj):
        return  ','.join(obj.selected_weekdays)
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
