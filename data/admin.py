from django.contrib import admin

from data.models import Country, Airport, AircraftType, Aircraft, Airline, Pilot, Steward


@admin.register(Country)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Airport)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['name', 'iata_code', 'icao_code', 'lat', 'lng', 'country']


@admin.register(AircraftType)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['model', 'icao_code']


@admin.register(Airline)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['name', 'iata_code', 'icao_code']


@admin.register(Aircraft)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['reg', 'model', 'airline', 'hub', 'status']


@admin.register(Pilot)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'patronymic', 'sex', 'type_pilot']


@admin.register(Steward)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'patronymic', 'sex']
    
