from django.conf.urls import url

from rate import  views
urlpatterns=[
    url(r'^rate_film', views.rate_film, name='rate-film'),
    url(r'^rate_page',views.rate_page, name='rate-page'),
]