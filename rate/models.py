from django.db import models

from cinema_place.models import Film
from general.models import CinemaUser
from rate.managers import RateManager


class Rate(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    user = models.ForeignKey(CinemaUser, on_delete=models.SET_NULL, null=True)
    value = models.SmallIntegerField()
    objects = RateManager()
    class Meta:
        unique_together = ('film', 'user')

