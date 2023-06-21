from django.contrib import admin
from .models import Floor, Room, Workplace, Booking, Status


class FloorAdmin(admin.ModelAdmin):
    model = Floor
    list_display = ('id', 'name',)


class RoomAdmin(admin.ModelAdmin):
    model = Room
    list_display = ('id', 'floor', 'name', 'rows', 'columns',
                    'index_on_map',
                    'area_x1', 'area_y1', 'area_x2', 'area_y2'
                    )

    fieldsets = (
        ('Main info', {'fields': ('id', 'floor', 'name')}),
        ('Room info', {'fields': ('rows', 'columns')}),
        ('SVG info', {'fields': ('index_on_map', 'area_x1', 'area_y1', 'area_x2', 'area_y2')}),
    )


class WorkplaceAdmin(admin.ModelAdmin):
    model = Workplace
    list_display = ('id', 'room', 'index', 'column_id', 'row_id', 'is_available',)


class BookingAdmin(admin.ModelAdmin):
    model = Booking
    list_display = ('id', 'workplace', 'user', 'date',)


class StatusAdmin(admin.ModelAdmin):
    model = Status
    list_display = ('id', 'name', 'color',)


# Register your models here.
admin.site.register(Floor, FloorAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Status, StatusAdmin)
