from django.db import models

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




class Session(models.Model):
    film_cinema = models.ForeignKey(FilmCinema, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    hall = models.ForeignKey(CinemaHall)


class ReservationSeat(models.Model):
    booked = models.BooleanField(default=False)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)


class Ticket(models.Model):
    tree_dimensional = models.BooleanField()
    reservation_seat = models.OneToOneField(ReservationSeat,on_delete=models.CASCADE)
    price = models.SmallIntegerField()


class Reservation(models.Model):
    name = models.CharField(max_length=20, null=True)
    surname = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.ticket.reservation_seat.booked = True
        return super(Reservation, self).save(self, *args, **kwargs)
