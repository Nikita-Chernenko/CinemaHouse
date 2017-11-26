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
from cities_light.models import City
from django.core.files import File

from cinema_place.models import Film, Genre, Actor, Director, Brand, Area, Cinema


class QuotesSpider(scrapy.Spider):
    name = "cinemas"

    def start_requests(self):
        urls = [
            'https://kinoafisha.ua/cinema/harkov/',
            'https://kinoafisha.ua/cinema/kiev/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        url = response.url
        cinemas = response.css('.item')
        response = response.css('.item')
        for cinema in cinemas:
            name = cinema.xpath('.//h3//text()').extract_first()
            address = cinema.xpath('.//p[contains(text(),"Адрес:")]/span/text()').extract_first()
            phone = cinema.xpath('.//p[contains(text(),"Телефон:")]/span/text()').extract_first()
            image_url = cinema.xpath('.//img/@src').extract_first()
            if name and address and phone and image_url:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urllib.request.urlopen('https://kinoafisha.ua' + image_url).read())
                img_temp.flush()
                brand = get_object_or_None(Brand, name=name)
                if not brand:
                    brand = Brand(name=name)
                    brand.image.save(image_url.split('/')[-1], File(img_temp))
                    brand.save()
                city_dict = {'harkov': 'Kharkiv', 'kiev': 'Kyiv'}
                city_name = city_dict[url.split('/')[-2]]
                print(city_name)
                print('get_city')
                city = City.objects.get(name=city_name, country__name='Ukraine')
                print('got_city')
                print(city)

                area = get_object_or_None(Area, city=city, address=address)
                if not area:
                    area = Area(city=city, address=address, phone=phone)
                    area.save()
                cinema = get_object_or_None(Cinema, area=area, brand=brand)
                if not cinema:
                    cinema = Cinema(area=area, brand=brand)
                    cinema.save()

                yield {
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'image_url': image_url
                }
