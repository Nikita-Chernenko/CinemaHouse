from datetime import datetime, timedelta

from cities_light.models import City, Country
from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geos import Point
from django.core.serializers import json
from annoying.functions import get_object_or_None
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse

from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string

from cinema_place.models import Cinema, Film, FilmCinema, Genre
from rate.models import Rate
from rate.views import get_recommendations
from reservation.models import Session


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


def get_pic(request, url):
    print(url)
    image = open(url, 'rb').read()
    return HttpResponse(image, content_type='image/jpg')


def get_city_by_country_id(request):
    if request.method == "GET":
        try:
            country_id = request.GET['country_id']
        except:
            return Http404()
        cities = list(City.objects.filter(country_id=country_id).values_list('id', 'name'))
        return JsonResponse({'cities': cities})


def main(request):
    geo = GeoIP2()
    client_ip = get_client_ip(request)
    client_ip = '178.165.21.85'
    city = geo.city(client_ip)
    city = City.objects.get(area__country__name=city['country_name'], name=city['city'])
    recommedations = get_recommendations(request)
    films = Film.objects.all()
    if 'films_ids' in recommedations:
        films = films.exclude(pk__in=recommedations['films_ids'])

    return render(request, 'cinema_place/main_films.html', {'films': films,'recommendations':recommedations})


def get_cinemas_with_sessions_by_film(request, film_slug):
    city_id = request.GET['city']
    date = request.GET['date']
    film = Film.objects.get(slug=film_slug)
    cinemas = Cinema.objects.filter(filmcinema__film=film).filter(area__city_id=city_id)
    cinemas_with_sessions = []
    for cinema in cinemas:
        sessions = Session.objects.filter(film_cinema__cinema=cinema)
        sessions = sessions.filter(datetime__contains=date)
        cinemas_with_sessions.append({cinema: sessions})
    countries = Country.objects.all().values_list('id', 'name')
    return render(request, 'cinema_place/cinemas_with_sessions.html', {'cinemas_with_sessions': cinemas_with_sessions})


def search_cinemas_with_sessions(request, film_slug):
    city = _get_request_city(request)
    date = str(Session.objects.last().datetime.date())
    countries = Country.objects.all().values_list('id', 'name')
    cities = City.objects.filter(country=city.country).values_list('id', 'name')
    return render(request, 'cinema_place/search_cinemas_with_sessions.html',
                  {'countries': countries, 'cities': cities, 'country': city.country.name,
                   'city': city.name, 'film_slug': film_slug, 'date': date})


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
        print(genres)
        films = Film.objects.all()
        if name:
            films = films.filter(Q(name__contains=name)|Q(name__contains=name.capitalize()))
        if age_from:
            films = films.filter(age__gte=age_from)
        if age_to:
            films = films.filter(age__lte=age_to)
        if genres:
            films = films.filter(genres__in=genres).distinct()
        return render_to_response('cinema_place/film_thumbnail.html', {'films': films})
    else:
        genres = Genre.objects.all().values_list('id', 'name')
        return render(request, 'cinema_place/films.html', {'genres': genres}, )


def film_detail(request, film_slug):
    film = Film.objects.get(slug=film_slug)
    rated_by_user = None
    if request.user.is_authenticated():
        rated_by_user = get_object_or_None(Rate,film=film,user=request.user)
    return render(request, 'cinema_place/film_detail.html', {'film': film,'rated_by_user':rated_by_user})


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


def cinema_detail(request, cinema_slug):
    cinema = Cinema.objects.get(slug=cinema_slug)
    if request.method == "POST":
        date = request.POST['date']
        films_in_cinema = FilmCinema.objects.filter(cinema=cinema).filter(session__datetime__contains=date)

        films_with_sessions = {film_cinema.film: film_cinema.session_set.all() for film_cinema in films_in_cinema}

        return render(request, 'cinema_place/films_with_sessions.html', {'films_with_sessions': films_with_sessions})
    filmnames = [film.name for film in
                 Film.objects.filter(filmcinema__cinema=cinema, filmcinema__end_screening__gte=datetime.now().date())]
    date_start = datetime.now().date().strftime("%Y-%m-%d")
    date_end = (datetime.now().date() + timedelta(days=14)).strftime("%Y-%m-%d")
    return render(request, 'cinema_place/cinema_detail.html',
                  {'cinema': cinema, 'filmnames': filmnames, 'date_start': date_start, 'date_end': date_end})

