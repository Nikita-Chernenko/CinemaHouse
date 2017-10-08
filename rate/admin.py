from django.contrib import admin

from rate.models import Rate



@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    pass
