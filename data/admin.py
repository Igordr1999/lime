from django.contrib import admin
from data.models import Country, Airport, AircraftType, Aircraft, Airline, Pilot, Steward, Route, Flight


@admin.register(Country)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority']


@admin.register(Airport)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['name', 'iata_code', 'icao_code', 'lat', 'lng', 'country', 'priority']


@admin.register(AircraftType)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['model', 'icao_code', 'priority']


@admin.register(Airline)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['name', 'iata_code', 'icao_code', 'priority']


@admin.register(Aircraft)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['reg', 'model', 'airline', 'hub', 'status']


@admin.register(Pilot)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'patronymic', 'sex', 'type_pilot', 'hub', 'airline']


@admin.register(Steward)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'patronymic', 'sex', 'hub']


@admin.register(Route)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['number', 'from_airport', 'to_airport', 'airline', 'days_of_week', 'is_international', 'is_regular']


@admin.register(Flight)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["route", "from_datetime", "to_datetime"]
