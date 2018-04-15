from django import forms
from django.contrib.auth.models import User
from data.models import Country, Airport, AircraftType, Aircraft, Airline, Pilot, Steward


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')


class AirlineForm(forms.ModelForm):
    class Meta:
        model = Airline
        fields = ('name', 'iata_code', 'icao_code', 'logo')


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = '__all__'
