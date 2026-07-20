from django.contrib import admin
from django.db import models

from common.fields import CommaDecimalFormField
from .models import City, Country, State


class CommaDecimalAdminMixin:
    formfield_overrides = {
        models.DecimalField: {"form_class": CommaDecimalFormField},
    }


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "code"]
    search_fields = ["name", "code"]


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "country"]
    search_fields = ["name"]
    list_filter = ["country"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "state"]
    search_fields = ["name"]
    list_filter = ["state"]
