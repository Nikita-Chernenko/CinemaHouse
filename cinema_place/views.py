from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geos import Point
from django.core.serializers import json
from django.http import HttpResponse

from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string

from cinema_place.models import Cinema, FilmImage


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home(request):
    g = GeoIP2()
    client_ip = get_client_ip(request)
    client_ip = '178.165.21.85'
    lat,lon = g.lat_lon(client_ip)
    waypoints = Cinema.objects.all()
    return render_to_response('cinema_place/home.html', {
        'waypoints': waypoints,
        'content': render_to_string('cinema_place/cinema_map.html', {'waypoints': waypoints}),
    })


def get_pic(request,url):
    print(url)
    image = open(url,'rb').read()
    return HttpResponse(image,content_type='image/jpg')
