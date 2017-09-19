from django.contrib import admin
from cinema_place.models import Cinema, Area, Film, FilmCinema, FilmImage, Brand
from django.contrib.gis import admin as geoadmin
from django.contrib.gis.db import models
from mapwidgets.widgets import GooglePointFieldWidget

@admin.register(Cinema, Area, Film, FilmCinema, Brand)
class CinemaPlaceAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }

@admin.register(FilmImage)
class FilmPictureAdmin(admin.ModelAdmin):
    fields = ('image_tag','film','image')
    readonly_fields = ('image_tag',)
