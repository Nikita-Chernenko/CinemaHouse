import datetime

from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from reservation.forms import ReservationForm
from reservation.models import Session, Seat, ReservationSeat,  SessionSeatTypePrice, Ticket


@render_to('reservation/seat_table.html')
def get_reservation_by_session_id(request, session_id):
    session = Session.objects.get(pk=session_id)
    seats = Seat.objects.filter(cinema_hall=session.hall)
    reserved_seats = [seat.seat for seat in ReservationSeat.objects.filter(session_id=session_id)]
    seats_in_rows = [[seats[0]]]
    index = 0
    for x in range(1, len(seats)):
        seats[x].booked = seats[x] in reserved_seats
        seats[x].price = SessionSeatTypePrice.objects.get(seat_type=seats[x].type, session=session).price
    for x in range(1, len(seats)):
        if seats[x].row == seats[x - 1].row:
            seats_in_rows[index].append(seats[x])
        else:
            index += 1
            seats_in_rows.append([seats[x]])
    film_name = session.film_cinema.film.name
    datetime = session.datetime_start
    return {'seats_in_rows': seats_in_rows, 'film_name': film_name, 'datetime': datetime,
            'session_id': session_id}


def continue_reservation(request, reservation_seat_ids, session_id):
    session = Session.objects.get(pk=session_id)
    seat_ids = reservation_seat_ids.split(',')
    seats = []
    price = 0
    for id in seat_ids:
        seat = get_object_or_None(Seat, pk=id)
        r = get_object_or_None(ReservationSeat, session=session, seat=seat)
        if not r:
            seats.append(seat)
            price += SessionSeatTypePrice.objects.get(seat_type=seat.type, session=session).price

    if seats:
        film_name = session.film_cinema.film.name
        date_time_start = session.datetime_start
        date_time_end = session.datetime_end
    else:
        return redirect(request.META['HTTP_REFERER'])
    if request.method == 'POST':
        form = ReservationForm(request.POST)

        if form.is_valid():
            tickets = []
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            email = form.cleaned_data['email']
            ticket = Ticket(name=name, surname=surname, email=email)
            ticket.save()
            for seat in seats:
                r = ReservationSeat(session=session, seat=seat, ticket=ticket)
                r.save()
                tickets.append(r)
            send_mail("Регестрация билета", f'Здравствуйте {name} {surname}.'
                                            f'Вы заказали билеты в количестве {len(tickets)}. Номер заказа - {ticket.id}'
                                            f' на фильм {film_name} который пройдет'
                                            f' {datetime.datetime.strftime(date_time_start,"%m.%d %a %H:%M")} - {datetime.datetime.strftime(date_time_end,"%H:%M")}.'
                                            f'Вы можете оплатить билеты на кассе. '
                                            f'Помните, пока вы только забронировали билеты, их нужно выкупить',
                      'СinemaHouse+', [email], )
            return redirect(reverse('main'))
    form = ReservationForm()
    return render(request, 'reservation/reservation.html',
                  {'seats': seats, 'name': film_name, 'datetime': date_time_start, 'price': price,
                   'form': form, 'hall': session.hall.name,
                   'seat_ids': reservation_seat_ids, 'session_id': session_id})
