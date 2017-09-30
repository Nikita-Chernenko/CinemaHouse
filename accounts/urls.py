from django.conf.urls import url, include
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy

from accounts import views

urlpatterns =[
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout', views.my_logout, name='logout'),
    url(r'change_password$', PasswordChangeView.as_view(), name='change_password'),
    url(r'^', include('registration.backends.hmac.urls')),
]