from django.contrib import admin
from django.contrib.admin import display
from .models import Flight, Scheme


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('scheme', 'index', 'date', 'van', 'gruj', 'start_road', 'destination_road', 'cost',
                    'downtime_loading', 'downtime_uploading', 'travel_time', 'distance_road', 'expenses',
                    'station_start_id', 'station_destination_id', 'get_profit', 'get_daily_profit')
    list_display_links = ('scheme', 'index', 'date', 'van',)
    search_fields = 'date', 'van', 'start_road', 'destination_road',
    list_filter = ('scheme', 'index', 'van')
    save_as = True
    save_on_top = True
    ordering = ('van', 'date', 'gruj',)

    @display(description='Доходность')
    def get_profit(self, obj):
        return obj.scheme.get_profit()

    @display(description='Доходность в сутки')
    def get_daily_profit(self, obj):
        return obj.scheme.get_daily_profit()


admin.site.register(Scheme)
