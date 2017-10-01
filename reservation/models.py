from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from cinema_place.models import FilmCinema, Cinema


class CinemaHall(models.Model):
    name = models.CharField(max_length=1)
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)

class SeatTypes(models.Model):
    type = models.CharField(max_length=20)

class Seat(models.Model):
    cinema_hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE)
    row = models.SmallIntegerField()
    seat = models.SmallIntegerField()
    type = models.ForeignKey(SeatTypes)

    def __str__(self):
        return f'Ряд {self.row} место {self.seat}'




class Session(models.Model):
    film_cinema = models.ForeignKey(FilmCinema, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    hall = models.ForeignKey(CinemaHall)


class ReservationSeat(models.Model):
    booked = models.BooleanField(default=False)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.seat}'


class Ticket(models.Model):
    three_dimensional = models.BooleanField()
    reservation_seat = models.OneToOneField(ReservationSeat,on_delete=models.CASCADE)
    price = models.SmallIntegerField()

    def __str__(self):
        return f'{self.reservation_seat} {self.price}'


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

@receiver(post_save,sender=Reservation)
def reservation_post_save(sender, instance, created, **kwargs):
    if instance.tickets:
        for ticket in instance.tickets.all():
            ticket.reservation_seat.booked=True
            ticket.reservation_seat.save()
            ticket.save()

