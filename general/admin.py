from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from general.models import CinemaUser


class CinemaAdmin(UserAdmin):
    pass

admin.site.register(CinemaUser, CinemaAdmin)