from registration.forms import RegistrationForm

from general.models import CinemaUser


class CinemaUserForm(RegistrationForm):
    class Meta:
        model = CinemaUser
        fields = ["username", "email"]

