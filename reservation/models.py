import datetime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from cinema_place.models import FilmCinema, Cinema


class CinemaHall(models.Model):
    name = models.CharField(max_length=10)
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)


class SeatType(models.Model):
    type = models.CharField(max_length=20)


class Seat(models.Model):
    cinema_hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE)
    row = models.SmallIntegerField()
    seat = models.SmallIntegerField()
    type = models.ForeignKey(SeatType)

    def price(self, session):
        return self.type.sessionseattypeprice_set.get(session=session).price

    def __str__(self):
        return f'Ряд {self.row} место {self.seat}'

    class Meta:
        ordering = ['row', 'seat']


class Session(models.Model):
    film_cinema = models.ForeignKey(FilmCinema, on_delete=models.CASCADE)
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    hall = models.ForeignKey(CinemaHall)
    prices = models.ManyToManyField(SeatType, through='SessionSeatTypePrice')
    three_dimensional = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.datetime_end:
            self.datetime_end = self.datetime_start + datetime.timedelta(
                minutes=self.film_cinema.film.duration_minutes + 15)
        # sessions = Session.objects.filter(film_cinema=self.film_cinema, hall=self.hall)
        # start = self.datetime_start
        # end = self.datetime_end
        # if any([True for x in sessions if x.datetime_start > start and x.datetime_end < end or
        #                         x.datetime_start < start and x.datetime_end > start or
        #                         x.datetime_start < end and x.datetime_end > end]):
        #     raise ValueError('session in this time exists')
        super(Session, self).save(*args, **kwargs)


class SessionSeatTypePrice(models.Model):
    session = models.ForeignKey(Session)
    seat_type = models.ForeignKey(SeatType)
    price = models.SmallIntegerField()

    class Meta:
        unique_together = ['session', 'seat_type']


class Ticket(models.Model):
    name = models.CharField(max_length=20, null=True)
    surname = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)

    @property
    def summary(self):
        return self.reservationseat_set.all().aggregate(sum('price'))

    def __str__(self):
        return f'{self.name} {self.surname} '


class ReservationSeat(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    @property
    def price(self):
        seat_type = self.seat.type.type
        print(seat_type)
        return self.session.sessionseattypeprice_set.get(seat_type__type=seat_type).price

    def __str__(self):
        return f'{self.seat}'
