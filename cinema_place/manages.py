from datetime import datetime

from django.db import models

class FilmManager(models.Manager):
    def active(self):
        active_films = self.filter(active=True)
        for film in active_films:
            if not any(film_cinema.end_screening >= datetime.now().date() for film_cinema in  film.filmcinema_set.all()):
                film.active = False
                film.save()
        return self.filter(active=True)
