from django.contrib import admin

from cinema_place.models import Cinema, Area, Film, FilmCinema, Brand, Genre, Actor, Director
from django.contrib.gis import admin as geoadmin
from django.contrib.gis.db import models
from mapwidgets.widgets import GooglePointFieldWidget

CUSTOM_MAP_SETTINGS = {
    "GooglePointFieldWidget": (
        ("zoom", 5),
        ("mapCenterLocationName", "london"),
        ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'uk'}}),
        ("markerFitZoom", 12),
    ),
}


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget(settings=CUSTOM_MAP_SETTINGS)}
    }


@admin.register(Film)
class RateAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['genres']
    list_display = ['name', 'rate', 'duration_minutes', 'date_release']
    readonly_fields = ('rate', 'slug')


@admin.register(Genre, Actor, Director, Cinema, FilmCinema)
class CinemaPlaceAdmin(admin.ModelAdmin):
    pass


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    fields = ('name', 'image', 'image_url')
    readonly_fields = ('image_url',)
