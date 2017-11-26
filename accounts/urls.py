from django.conf.urls import url, include
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy
from registration.backends.hmac.views import RegistrationView

from accounts import views
from accounts.forms import CinemaUserForm

urlpatterns = [
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout', views.my_logout, name='logout'),
    url(r'^change_password$', PasswordChangeView.as_view(), name='change_password'),
    url(r'^register/$',
        RegistrationView.as_view(
            form_class=CinemaUserForm
        ),
        name='registration_register',
        ),
    url(r'^', include('registration.backends.hmac.urls')),
]
