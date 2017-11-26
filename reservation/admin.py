from django.contrib import admin
from reservation.models import CinemaHall,Ticket,SeatType,Seat,ReservationSeat,Session


@admin.register(CinemaHall,Ticket,SeatType,Seat,ReservationSeat,Session)
class ReservationAdmin(admin.ModelAdmin):
    pass