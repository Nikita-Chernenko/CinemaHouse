import csv
from datetime import datetime, timedelta
from itertools import groupby

from annoying.decorators import render_to
from cities_light.models import City, Country
from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geos import Point
from django.core.serializers import json
from annoying.functions import get_object_or_None
from django.db.models import Q, Sum
from django.http import HttpResponse, Http404, JsonResponse

from django.shortcuts import render, render_to_response, get_object_or_404
from django.template.loader import render_to_string
from functools import reduce

from CinemaHouse import settings
from cinema_place.models import Cinema, Film, FilmCinema, Genre
from rate.models import Rate
from rate.views import get_recommendations
from reservation.models import Session, ReservationSeat


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if ip == '127.0.0.1':
        ip = '178.165.21.85'
    return ip


def home(request):
    g = GeoIP2()
    client_ip = get_client_ip(request)
    lat, lon = g.lat_lon(client_ip)
    waypoints = Cinema.objects.all()
    return render_to_response('cinema_place/home.html', {
        'waypoints': waypoints,
        'content': render_to_string('cinema_place/cinema_map.html', {'waypoints': waypoints}),
    })


def get_pic(request, url, type):
    try:
        image = open(url, 'rb').read()
    except FileNotFoundError:
        if type == 'film':
            image = open(f'{settings.MEDIA_ROOT}/film_default.jpg', 'rb').read()
        if type == 'cinema':
            image = open(f'{settings.MEDIA_ROOT}/cinema_default.jpg', 'rb').read()

    return HttpResponse(image, content_type='image/jpg')


def get_city_by_country_id(request):
    if request.method == "GET":
        try:
            country_id = request.GET['country_id']
        except:
            return Http404()
        cities = list(City.objects.filter(country_id=country_id).values_list('id', 'name'))
        return JsonResponse({'cities': cities})


@render_to('cinema_place/main_films.html')
def main(request):
    geo = GeoIP2()
    client_ip = get_client_ip(request)
    client_ip = '178.165.21.85'
    city = geo.city(client_ip)
    city = City.objects.get(country__name=city['country_name'], name=city['city'])
    recommedations = get_recommendations(request)
    films = Film.objects.all()
    if 'films_ids' in recommedations:
        films = films.exclude(pk__in=recommedations['films_ids'])

    return {'films': films, 'recommendations': recommedations}


@render_to('cinema_place/cinemas_with_sessions.html')
def get_cinemas_with_sessions_by_film(request, film_slug):
    city_id = request.GET['city']
    date = request.GET['date']
    film = Film.objects.get(slug=film_slug)
    cinemas = Cinema.objects.filter(filmcinema__film=film).filter(area__city_id=city_id)
    cinemas_with_sessions = []
    for cinema in cinemas:
        sessions = Session.objects.filter(film_cinema__cinema=cinema, film_cinema__film=film)
        sessions = sessions.filter(datetime_start__contains=date)
        cinemas_with_sessions.append({cinema: sessions})
    countries = Country.objects.all().values_list('id', 'name')
    return {'cinemas_with_sessions': cinemas_with_sessions}


@render_to('cinema_place/search_cinemas_with_sessions.html')
def search_cinemas_with_sessions(request, film_slug):
    city = _get_request_city(request)
    date = str(Session.objects.last().datetime_start.date() if Session.objects.last() else datetime.today().date())
    countries = Country.objects.all().values_list('id', 'name')
    cities = City.objects.filter(country=city.country).values_list('id', 'name')
    return {'countries': countries, 'cities': cities, 'country': city.country.name,
            'city': city.name, 'film_slug': film_slug, 'date': date}


def _get_request_city(request):
    g = GeoIP2()
    lon, lat = g.lon_lat(get_client_ip(request))
    city = City.objects.get(longitude__gt=lon - 0.0001, longitude__lt=lon + 0.0001, latitude__gt=lat - 0.0001,
                            latitude__lt=lat + 0.0001)
    return city


def films(request):
    if request.method == 'POST':
        name = request.POST['name']
        age_from = request.POST['age_from']
        age_to = request.POST['age_to']
        genres = request.POST.getlist('genres[]')
        films = Film.objects.all()
        if name:
            films = films.filter(Q(name__contains=name) | Q(name__contains=name.capitalize()))
        if age_from:
            films = films.filter(age__gte=age_from)
        if age_to:
            films = films.filter(age__lte=age_to)
        if genres and all(genres):
            films = films.filter(genres__in=genres).distinct()
        return render_to_response('cinema_place/film_thumbnail.html', {'films': films})
    else:
        genres = Genre.objects.all().values_list('id', 'name')
        return render(request, 'cinema_place/films.html', {'genres': genres}, )


@render_to('cinema_place/film_detail.html')
def film_detail(request, film_slug):
    film = Film.objects.get(slug=film_slug)
    rated_by_user = None
    if request.user.is_authenticated():
        rated_by_user = get_object_or_None(Rate, film=film, user=request.user)
    return {'film': film, 'rated_by_user': rated_by_user}


def cinemas(request):
    if request.method == 'POST':
        city_id = request.POST['city_id']
        cinemas = Cinema.objects.filter(area__city_id=city_id)
        cinemas_with_films = {
            cinema: [filmcinema.film.name for filmcinema in FilmCinema.objects.filter(cinema=cinema) if
                     filmcinema.end_screening > datetime.now().date()][:5]
            for cinema in cinemas}

        return render(request, 'cinema_place/cinemas_with_films.html', {'cinemas_with_films': cinemas_with_films})
    city = _get_request_city(request)
    countries = Country.objects.all().values_list('id', 'name')
    cities = City.objects.filter(country=city.country).values_list('id', 'name')
    return render(request, 'cinema_place/cinemas.html',
                  {'countries': countries, 'cities': cities, 'country': city.country.name,
                   'city': city.name})


@render_to('cinema_place/cinema_detail.html')
def cinema_detail(request, cinema_slug):
    cinema = Cinema.objects.get(slug=cinema_slug)
    if request.method == "POST":
        date = request.POST['date']
        films_in_cinema = FilmCinema.objects.filter(cinema=cinema).filter(session__datetime_start__contains=date)

        films_with_sessions = {film_cinema.film: film_cinema.session_set.all() for film_cinema in films_in_cinema}

        return render(request, 'cinema_place/films_with_sessions.html', {'films_with_sessions': films_with_sessions})
    filmnames = [film.name for film in
                 Film.objects.filter(filmcinema__cinema=cinema, filmcinema__end_screening__gte=datetime.now().date())][
                :40]
    date_start = datetime.now().date().strftime("%Y-%m-%d")
    date_end = (datetime.now().date() + timedelta(days=14)).strftime("%Y-%m-%d")
    return {'cinema': cinema, 'filmnames': filmnames, 'date_start': date_start, 'date_end': date_end}


def cinema_timetable(request, cinema_slug):
    cinema = get_object_or_404(Cinema, slug=cinema_slug)
    date = datetime.now().date()
    sessions = list(Session.objects.filter(film_cinema__cinema=cinema, datetime_start__contains=date).select_related(
        'film_cinema__film__name'). \
                    order_by('film_cinema__film__name', 'datetime_start').values_list('film_cinema__film__name',
                                                                                      'datetime_start',
                                                                                      'datetime_end'))

    timetable = []
    ind = 0
    for film, time in groupby(sessions, lambda x: x[0]):
        timetable.append([film])
        for time in time:
            timetable[ind].append(f'{time[1].strftime("%H:%M")} -{time[2].strftime("%H:%M")}')
        ind += 1

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="timetable-{cinema.brand.name}-{date}"'
    writer = csv.writer(response)
    for film_time in timetable:
        writer.writerow(film_time)
    return response


def cinema_money(request):
    date_now = datetime.now()
    cinemas = Cinema.objects.all()
    cinema_m = {}
    for cinema in cinemas:
        rs = ReservationSeat.objects. \
            filter(session__datetime_end__contains=date_now.month).filter(
            session__film_cinema__cinema=cinema)
        rs = [r.price for r in rs]
        cinema_m[cinema.brand.name + '-' + str(cinema.id)] = reduce(lambda x, y: x + y, rs if rs else [0])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="cinema-money-{date_now}"'
    writer = csv.writer(response)
    writer.writerow(['Кинотеатр','Сумма за месяц'])
    for key, value in cinema_m.items():
        writer.writerow([key,str(value)+' грн'])
    return response
