#!/usr/bin/env python
# -*- coding: utf-8
import re
import shutil
import urllib
from tempfile import TemporaryFile, NamedTemporaryFile
from urllib.request import urlretrieve

import requests as requests
import scrapy
from datetime import date

from annoying.functions import get_object_or_None
from django.core.files import File

from cinema_place.models import Film, Genre, Actor, Director


class QuotesSpider(scrapy.Spider):
    name = "films"

    def start_requests(self):
        urls = [
            'https://kinoafisha.ua/kinoafisha/harkov/',
            'https://kinoafisha.ua/kinoafisha/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        films = response.css('.item').xpath('//h3/a/@href').extract()
        for link in films:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_film)

    def parse_film(self, response):
        name = response.xpath('//h1/span/text()').extract_first()
        description = response.css('.description').xpath('.//p/text()').extract_first()
        age = response.css('.thumbHolder .agerate::text').extract_first()
        video_url = response.css('#videoHolder').xpath('iframe/@src').extract()
        response = response.css('.film-detail')
        genres = response.xpath('.//p[contains(text(),"Жанр")]/a/text()').extract()
        cast = response.xpath('.//p[contains(text(),"Актёры")]//text()').extract()
        directors = response.xpath('.//p[contains(text(),"Режиссёр")]//text()').extract()
        duration = response.xpath('.//p[contains(text(),"Продолжительность")]/span[1]/text()').extract_first()
        image_url = response.css('.thumbHolder').xpath('.//a//img/@src').extract_first()
        required = [name, description, genres, cast, directors]
        genres = list(filter(lambda x: x.strip() not in [',', '...', '.', ''], genres))[1:]
        cast = list(filter(lambda x: x.strip() not in [',', '...', '.', ''], cast))[1:]
        directors = list(filter(lambda x: x.strip() not in [',', '...', '.', ''], directors))[1:]
        if description:
            description.replace('\n','')
        if age:
            age = age[:-1]
        if duration:
            duration = re.findall(r'[0-9]{1,2}', duration)
            if not duration:
                duration.append(0)
            if len(duration) == 1:
                duration.append(0)
            duration = int(duration[0]) * 60 + int(duration[1])
        if all(required):
            _genres = []
            _cast = []
            _directors = []
            for genre in genres:
                g = get_object_or_None(Genre, name=genre)
                if not g:
                    g = Genre(name=genre)
                    g.save()
                _genres.append(g)
            for actor in cast:
                g = get_object_or_None(Actor, name_surname=actor)
                if not g:
                    g = Actor(name_surname=actor)
                    g.save()
                _cast.append(g)
            for director in directors:
                g = get_object_or_None(Director, name_surname=director)
                if not g:
                    g = Director(name_surname=director)
                    g.save()
                _directors.append(g)
            if not age:
                age = 3

            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib.request.urlopen('https://kinoafisha.ua' + image_url).read())
            img_temp.flush()

            film = Film(name=name, description=description,
                        date_release=date.today(), age=age, duration_minutes=duration, video_url=video_url)
            film.vertical_image.save(image_url.split('/')[-1], File(img_temp))
            film.horizontal_image.save(image_url.split('/')[-1], File(img_temp))
            film.big_image.save(image_url.split('/')[-1], File(img_temp))
            print(_cast)
            print(_directors)
            print(_genres)
            for actor in _cast:
                film.cast.add(actor)
            for director in _directors:
                film.directors.add(director)
            for genre in _genres:
                film.genres.add(genre)
            film.save()

        yield {
            # 'film_name': name,
            # 'genres': genres,
            'description': description,
            # 'age': age,
            # 'cast': cast,
            # 'producers': producers,
            # 'video_url': video_url,
            # 'duration': duration,
            # 'image_url': image_url,
        }
