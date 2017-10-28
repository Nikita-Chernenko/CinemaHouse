import datetime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from cinema_place.models import FilmCinema, Cinema


class CinemaHall(models.Model):
    name = models.CharField(max_length=1)
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
            self.datetime_end = self.datetime_start + datetime.timedelta(minutes=self.film_cinema.film.duration_minutes)
        super(Session, self).save(*args, **kwargs)  # TODO test it


class SessionSeatTypePrice(models.Model):
    session = models.ForeignKey(Session)
    seat_type = models.ForeignKey(SeatType)
    price = models.SmallIntegerField()

    class Meta:
        unique_together = ['session', 'seat_type']


class ReservationSeat(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.seat}'


class Ticket(models.Model):
    reservation_seat = models.OneToOneField(ReservationSeat, on_delete=models.CASCADE)
    bar = models.ImageField(upload_to='bar_codes', unique=True, null=True)

    @property
    def price(self):
        seat_type = self.reservation_seat.seat.type.type
        print(seat_type)
        return self.reservation_seat.session.sessionseattypeprice_set.get(seat_type__type=seat_type).price

    def __str__(self):
        return f'{self.reservation_seat}'


class Reservation(models.Model):
    name = models.CharField(max_length=20, null=True)
    surname = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    tickets = models.ManyToManyField(Ticket)

    @property
    def summary(self):
        return self.tickets.all().aggregate(sum('price'))

    def __str__(self):
        return f'{self.name} {self.surname} {self.tickets.all()}'


@receiver(post_save, sender=Reservation)
def reservation_post_save(sender, instance, created, **kwargs):
    if instance.tickets:
        for ticket in instance.tickets.all():
            ticket.reservation_seat.booked = True
            ticket.reservation_seat.save()
            ticket.save()
