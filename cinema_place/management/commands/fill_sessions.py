import random

from annoying.functions import get_object_or_None
from datetime import date, datetime
import datetime as dt
from django.core.management import BaseCommand
from django.db import transaction

from cinema_place.models import Film, Cinema, FilmCinema
from reservation.models import CinemaHall, SeatType, Seat, Session, SessionSeatTypePrice


class Command(BaseCommand):
    help = 'fills db with sessions for today'

    def handle(self, *args, **options):
        # FilmCinema.objects.all().delete()
        # CinemaHall.objects.all().delete()
        # SeatType.objects.all().delete()
        # Seat.objects.all().delete()
        Session.objects.all().delete()
        SessionSeatTypePrice.objects.all().delete()
        films = Film.objects.all()
        cinemas = Cinema.objects.all()
        FilmCinema.objects.update(end_screening = date.today() + dt.timedelta(days=14))
        for film in films:
            for cinema in cinemas:
                film_cinema = get_object_or_None(FilmCinema, cinema=cinema, film=film)
                if not film_cinema:
                    film_cinema = FilmCinema.objects.create(cinema=cinema, film=film, start_screening=date.today(),

                                                            end_screening=date.today() + dt.timedelta(days=14))
        hall_types = "A"
        self.stdout.write('film_cinemas_done')
        for cinema in cinemas:
            for l in hall_types:
                hall = get_object_or_None(CinemaHall, cinema=cinema, name=l)
                if not hall:
                    hall = CinemaHall.objects.create(name=l, cinema=cinema)
        type_types = ['Normal', 'Premium']
        for type in type_types:
            st = get_object_or_None(SeatType, type=type)
            if not st:
                SeatType.objects.create(type=type)
        type_types = SeatType.objects.all()
        self.stdout.write('halls and seat_types done')
        counter = CinemaHall.objects.count()
        for ind,hall in enumerate(CinemaHall.objects.all()):
            for x in range(10):
                for y in range(10):
                    s = get_object_or_None(Seat, row=x, seat=y, cinema_hall=hall)
                    if not s:
                        type = type_types[0] if x < 9 else type_types[1]
                        s = Seat.objects.create(row=x, seat=y, cinema_hall=hall, type=type)
            self.stdout.write(f'{ind} out of  {counter}')
        self.stdout.write('seats done')
        year = datetime.today().year
        month = datetime.today().month
        day = datetime.today().day
        hour = 8
        minutes = 45
        min_delta = dt.timedelta(minutes=90)
        date_time = datetime(year, month, day, hour, minutes)
        date_times = []
        seat_types = SeatType.objects.all()
        counter = FilmCinema.objects.count()
        while date_time.hour < 11:
            date_times.append(date_time)
            date_time += min_delta
        for ind, film_cinema in enumerate(FilmCinema.objects.all()):
            halls = CinemaHall.objects.filter(cinema=film_cinema.cinema)
            for time in date_times:
                hall = random.choice(halls)
                _3d = random.choice([True, False])
                session = Session.objects.create(film_cinema=film_cinema, hall=hall, three_dimensional=_3d,
                                                 datetime_start=time)
                for st in seat_types:
                    SessionSeatTypePrice.objects.create(session=session, seat_type=st,
                                                        price=60 if st.type == 'Normal' else 80)
            if ind % 20 == 0:
                self.stdout.write(f'{ind} out of {counter} done')
