import datetime
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from reservation.forms import ReservationForm
from reservation.models import Session, Seat, ReservationSeat, Reservation


def get_reservation_by_session_id(request, session_id):
    # session = Session.objects.get(pk=session_id)
    seats = ReservationSeat.objects.filter(session_id=session_id).order_by('seat__row', 'seat__seat')

    seats_in_rows = [[seats[0]]]
    index = 0
    for x in range(1, len(seats)):
        if seats[x].seat.row == seats[x - 1].seat.row:
            seats_in_rows[index].append(seats[x])
        else:
            index += 1
            seats_in_rows.append([seats[x]])
    film_name = seats.first().session.film_cinema.film.name
    datetime = seats.first().session.datetime
    return render(request, 'reservation/seat_table.html',
                  {'seats_in_rows': seats_in_rows, 'film_name': film_name, 'datetime': datetime,
                   'session_id': session_id})


def continue_reservation(request, reservation_seat_ids, session_id):
    seat_ids = reservation_seat_ids.split(',')
    seats = []
    price = 0
    for id in seat_ids:
        try:
            r = ReservationSeat.objects.get(pk=int(id))
            if not r.booked:
                seats.append(r)
                price += r.ticket.price
        except:
            pass
    if seats:
        film_name = seats[0].session.film_cinema.film.name
        date_time = seats[0].session.datetime
    else:
        return HttpResponse("Bad Request")
    if request.method == 'POST':
        form = ReservationForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            email = form.cleaned_data['email']
            tickets = [seat.ticket for seat in seats]
            reservation = Reservation(name=name, surname=surname, email=email)
            reservation.save()
            for ticket in tickets:
                reservation.tickets.add(ticket)
            reservation.save()
            send_mail("Регестрация билета", f'Здравствуйте {name} {surname}.'
                                            f'Вы заказали билеты в количестве {len(tickets)}. Номер заказа - {reservation.id}'
                                            f' на фильм {film_name} который пройдет'
                                            f' {datetime.datetime.strftime(date_time,"%m %d %a %H %M")}.'
                                            f'Вы можете оплатить билеты на кассе. '
                                            f'Помните, пока вы только забронировали билеты, их нужно выкупить',
                      'СinemaHouse+', [email], )
            return redirect(reverse('main'))
    form = ReservationForm()
    return render(request, 'reservation/reservation.html',
                  {'reservation_seats': seats, 'name': film_name, 'datetime': date_time, 'price': price, 'form': form,
                   'seat_ids': reservation_seat_ids, 'session_id': session_id})
