from django.contrib import admin
from reservation.models import CinemaHall,Ticket,SeatTypes,Seat,ReservationSeat,Reservation,Session


@admin.register(CinemaHall,Ticket,SeatTypes,Seat,ReservationSeat,Reservation,Session)
class ReservationAdmin(admin.ModelAdmin):
    pass