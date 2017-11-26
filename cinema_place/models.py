import datetime

from django.db import models
from django.contrib.gis.db import models as gismodels
from cities_light.models import City, Country
from django.db.models import Avg, permalink
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse

from django.utils.safestring import mark_safe
from django.conf import settings

from cinema_place.managers import FilmManager
from general.models import CinemaUser



class Area(models.Model):
    city = models.ForeignKey(City)
    geom = gismodels.PointField(default='POINT(49.988358 36.232845)')
    phone = models.CharField(max_length=100, default="099-565-23-22")
    address = models.CharField(max_length=300)
    objects = gismodels.GeoManager()

    def __str__(self):
        return f"country: {self.city.country.name}, city: {self.city.name}"


class Brand(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='cinema_images', unique=True)


    def image_url(self):
        return f'/cinema/get_pic/{settings.MEDIA_ROOT}/{self.image}/cinema'

    image_url.short_description = 'Image'

    def __str__(self):
        return self.name


class Cinema(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    area = models.OneToOneField(Area, on_delete=models.CASCADE)
    slug = models.SlugField()
    allow_comments = models.BooleanField(default=True)

    def __str__(self):
        return f"Company name: {self.brand}  {self.area}  x:{self.area.geom.x} y:{self.area.geom.y}"

    def get_absolute_url(self):
        return reverse('cinema-detail', kwargs={'cinema_slug': self.slug})


@receiver(post_save, sender=Cinema)
def cinema_post_save(sender, instance, created, **kwargs):
    Cinema.objects.filter(pk=instance.id).update(slug=slugify(f'{instance.brand} {instance.id}'))


class Genre(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name}'


class Actor(models.Model):
    name_surname = models.CharField(max_length=40)
    image = models.ImageField(upload_to='actors', null=True, blank=True)

    def __str__(self):
        return f'{self.name_surname}'


class Director(models.Model):
    name_surname = models.CharField(max_length=40)
    image = models.ImageField(upload_to='produces', null=True, blank=True)

    def __str__(self):
        return f'{self.name_surname}'


class Film(models.Model):
    name = models.CharField(max_length=50)
    date_release = models.DateField()
    description = models.TextField()
    genres = models.ManyToManyField(Genre)
    slug = models.SlugField()
    age = models.SmallIntegerField(default=3)
    cast = models.ManyToManyField(Actor)
    directors = models.ManyToManyField(Director)
    vertical_image = models.ImageField(upload_to='film_images/vertical_images', unique=True)
    horizontal_image = models.ImageField(upload_to='film_images/gorizontal_images', unique=True)
    big_image = models.ImageField(upload_to='film_images/big_images', unique=True)
    video_url = models.URLField()
    allow_comments = models.BooleanField('allow_comments', default=True)
    active = models.BooleanField(default=True)
    duration_minutes = models.PositiveSmallIntegerField(default=120)

    objects = FilmManager()

    @property
    def vertical_image_url(self):
        return f'/cinema/get_pic/{settings.MEDIA_ROOT}/{self.vertical_image}/film'

    @property
    def horizontal_image_url(self):
        return f'/cinema/get_pic/{settings.MEDIA_ROOT}/{self.horizontal_image}/film'

    @property
    def big_image_url(self):
        return f'/cinema/get_pic/{settings.MEDIA_ROOT}/{self.big_image}/film'

    @property
    def rate(self):
        from rate.models import Rate
        return (Rate.objects.filter(film=self).aggregate(Avg('value')))['value__avg'] or 0

    def get_absolute_url(self):
        return reverse('film-detail', kwargs={'film_slug': self.slug})

    @property
    def short_description(self):
        return f'{self.description[:40]}...'

    def __str__(self):
        return f"film name: {self.name} desciption: {self.description[:30]}  data release: {self.date_release}"


@receiver(post_save, sender=Film)
def film_post_save(sender, instance, created, **kwargs):
    Film.objects.filter(pk=instance.id).update(slug=f'{"_".join(instance.name.split(" "))}_{instance.id}'.lower())


class FilmCinema(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    start_screening = models.DateField()
    end_screening = models.DateField()

    def __str__(self):
        return f"name: {self.film.name} cinema: {self.cinema.brand}"
