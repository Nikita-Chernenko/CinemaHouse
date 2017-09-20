from django.db import models
from django.contrib.gis.db import models as gismodels
from cities_light.models import City,Country
from django.utils.safestring import mark_safe
from django.conf import settings

class Area(models.Model):
    country = models.ForeignKey(Country)
    city = models.ForeignKey(City)
    def __str__(self):
        return f"country: {self.country.name}, city: {self.city.name}"

class Brand(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class Cinema(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    area = models.ForeignKey(Area,on_delete=models.CASCADE)
    geom = gismodels.PointField(default='POINT(49.988358 36.232845)')
    objects = gismodels.GeoManager()
    def __str__(self):
         return f"Company name: {self.brand}  {self.area}  x:{self.geom.x} y:{self.geom.y}"


class Film(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    def __str__(self):
        return  f"film name: {self.name} desciption: {self.description[:20]}"

class FilmImage(models.Model):
    film = models.ForeignKey(Film,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cinema_images',unique=True)

    def image_tag(self):
        return mark_safe('<img src=cinema/get_pic%s/%s width="150" height="150" />' %(settings.MEDIA_ROOT, self.image))
    image_tag.short_description = 'Image'

    def __str__(self):
        return  f" name: {self.film.name} image_url: {self.image}"

class FilmCinema(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    cinema = models.ForeignKey(Cinema,on_delete=models.CASCADE)
    date_release = models.DateField()
    def __str__(self):
        return  f"name: {self.film.name} cinema: {self.cinema.brand} data release: {self.date_release}"

