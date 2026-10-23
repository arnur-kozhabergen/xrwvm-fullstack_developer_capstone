from django.contrib import admin
from .models import CarMake, CarModel


class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 0


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    inlines = [CarModelInline]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ["name", "car_make", "type", "year"]
    list_filter = ["car_make", "type", "year"]
