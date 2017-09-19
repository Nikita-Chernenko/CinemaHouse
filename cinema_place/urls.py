from django.conf.urls import url

from cinema_place import  views
urlpatterns = [
    url(r'^home', views.home),
    url(r'^get_pic(?P<url>.*)', views.get_pic)
]