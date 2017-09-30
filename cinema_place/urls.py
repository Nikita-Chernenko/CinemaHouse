from django.conf.urls import url

from cinema_place import  views
urlpatterns = [
    url(r'^home', views.home),
    url(r'^get_pic/(?P<url>.*)', views.get_pic),
    url(r'^get_cinemas_with_sessions_by_film/(?P<film_slug>[\w\-0-9]+)', views.get_cinemas_with_sessions_by_film, name='get-cinemas-with-sessions-by-film'),
    url(r'^search_cinemas_with_sessions/(?P<film_slug>([\w\-0-9]+))', views.search_cinemas_with_sessions, name='search-cinemas-with-sessions'),
    url(r'^get_city_by_country_id', views.get_city_by_country_id, name='get-city-by-country-id'),
    url(r'^films$', views.films,name='films'),
    url(r'film_detail/(?P<film_slug>[\w\-0-9]+)', views.film_detail, name='film-detail'),
    url(r'^main$',views.main,name='main'),
]