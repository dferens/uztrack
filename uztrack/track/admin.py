from django.contrib import admin

from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from bitfield.admin import BitFieldListFilter

from .models import Way, TrackedWay


class WayAdmin(admin.ModelAdmin):
    list_display = ('station_from', 'station_till')
    list_filter = ('station_from', 'station_till')


class TrackedWayAdmin(admin.ModelAdmin):
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }
    list_filter = (
        ('days', BitFieldListFilter),
    )
    list_display = ('way', 'days_list')

    def days_list(self, obj):
        return  ','.join([x[0] for x in obj.days if x[1]])

    days_list.short_description = 'Days'


admin.site.register(Way, WayAdmin)
admin.site.register(TrackedWay, TrackedWayAdmin)