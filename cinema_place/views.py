from datetime import datetime

from cities_light.models import City, Country
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geos import Point
from django.core.serializers import json
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse

from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string

from cinema_place.models import Cinema, Film, FilmCinema, Genre
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
        cities = list(City.objects.filter(country_id=country_id).values_list('id','name'))
        return JsonResponse({'cities': cities})
def main(request):
    geo = GeoIP2()
    client_ip = get_client_ip(request)
    client_ip = '178.165.21.85'
    city = geo.city(client_ip)
    city = City.objects.get(area__country__name=city['country_name'], name=city['city'])
    films = Film.objects.all()
    return render(request, 'cinema_place/main_films.html', {'films': films})


def get_cinemas_with_sessions_by_film(request, film_slug):
    city_id = request.GET['city']
    date = request.GET['date']
    film = Film.objects.get(slug=film_slug)
    cinemas = Cinema.objects.filter(filmcinema__film=film).filter(area__city_id=city_id)
    cinemas_with_sessions = []
    for cinema in cinemas:
        sessions = Session.objects.filter(film_cinema__cinema=cinema)
        sessions = sessions.filter(datetime__contains = date)
        cinemas_with_sessions.append({cinema: sessions})
    countries = Country.objects.all().values_list('id','name')
    return render(request, 'cinema_place/cinemas_with_sessions.html', {'cinemas_with_sessions': cinemas_with_sessions})

def search_cinemas_with_sessions(request, film_slug):
    city = _get_request_city(request)
    date = str(Session.objects.last().datetime.date())
    countries = Country.objects.all().values_list('id','name')
    cities = City.objects.filter(country= city.country).values_list('id','name')
    return render(request, 'cinema_place/search_cinemas_with_sessions.html', {'countries':countries, 'cities': cities, 'country':city.country.name,
                                                               'city': city.name, 'film_slug':film_slug, 'date':date})
def _get_request_city(request):
    g = GeoIP2()
    lon, lat = g.lon_lat(get_client_ip(request))
    city = City.objects.get(longitude__gt=lon - 0.0001, longitude__lt=lon + 0.0001, latitude__gt=lat - 0.0001,
                            latitude__lt=lat + 0.0001)
    return city


def films(request):
    if request.method == 'POST':
        name = request.POST['name'].capitalize()
        age_from = request.POST['age_from']
        age_to = request.POST['age_to']
        genres =  request.POST.getlist('genres[]')
        films = Film.objects.all()
        if name:
            films = films.filter(name__contains=name)
        if age_from:
            films = films.filter(age__gte=age_from)
        if age_to:
            films = films.filter(age__lte=age_to)
        if genres:
            films = films.filter(genres__in=genres)
        return render_to_response('cinema_place/film_thumbnail.html',{'films':films})
    else:
        genres = Genre.objects.all().values_list('id','name')
        return render(request,'cinema_place/search_films.html',{'genres':genres},)
def film_detail(request, film_slug):
    film = Film.objects.get(slug=film_slug)
    return render(request,'cinema_place/film_detail.html',{'film': film})
