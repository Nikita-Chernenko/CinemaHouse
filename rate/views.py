from random import shuffle

import datetime
from annoying.functions import get_object_or_None
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

from cinema_place.models import Film, Genre, Actor
from rate.models import Rate


def rate_film(request):
    if request.user.is_authenticated() and request.method == "POST":
        user_rate = request.POST['rate']
        user = request.user
        film = Film.objects.get(pk=request.POST['film_id'])
        rate = get_object_or_None(Rate, film=film, user=user)
        if rate is None:
            Rate.objects.create(user=user, value=user_rate, film=film)
        else:
            rate.value = user_rate
            rate.save()
        return HttpResponse(film.rate)


def rate_page(request):
    time = datetime.datetime.now()
    user = request.user
    if user.is_authenticated():
        all_films = Film.objects.prefetch_related('genres')[:300]
        all_films = [film for film in all_films if not any([rate.user == user for rate in film.rate_set.all()])]
        sorted(all_films, key=lambda film: -film.rate)
        films_len = len(all_films)
        genres = [genre for genre in Genre.objects.all()]
        films_lim = 32
        ind = 0
        films = []
        iiii=0
        while ind < films_lim and ind < films_len:
            genre_ind = 0
            while genre_ind < len(genres):
                iiii+=1
                genre_films = [film for film in all_films if genres[genre_ind] in film.genres.all()]
                if len(genre_films) <= ind:
                    genres.remove(genres[genre_ind])
                    continue
                film = genre_films[ind]
                if film in films:
                    all_films.remove(film)
                    continue
                films.append(film)
                genre_ind += 1
            shuffle(genres)
            ind += 1
        return render(request, 'rate/rate_page.html', {'films': films})


def get_recommendations(request):
    if request.user.is_authenticated:
        films = Film.objects.active().prefetch_related('genres','cast','directors','rate_set')
        films = films.order_by('-rate')
        user = request.user
        rates = Rate.objects.for_user(user).order_by('-value')
        len_rates = len(rates)
        if len_rates >= 20:
            genres = list(rates.values_list('film__genres',flat=True).annotate(Count('film__genres'))[:2])
            actors = list(rates.values_list('film__cast',flat=True).annotate(Count('film__cast'))[:2])
            directors = list(rates.values_list('film__directors',flat=True).annotate(Count('film__directors'))[:2])
            films_by_genres = list(films.filter(genres__in=genres).distinct())[:5]
            films_by_actors = list(films.filter(cast__in=actors).distinct())
            films_by_directors  = list(films.filter(directors__in=directors).distinct())
            best_films = []
            best_films_count = 6 - len(films_by_genres) - len(films_by_actors) - len(films_by_directors)
            if best_films_count > 0:
                best_films = list(films[:best_films_count])
            films_list = [films_by_actors,films_by_genres,films_by_directors,best_films]
            recommendations = []
            for films in films_list:
                recommendations += [ film for film in films if film not in recommendations]
            shuffle(recommendations)
            return {'recommendations':recommendations}
        return {'films_to_get_recommendations':20 - len_rates}
    return []