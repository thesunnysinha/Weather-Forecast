# admin.py

from django.contrib import admin
from .models import FavoriteLocation

class FavoriteLocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country', 'user')
    list_filter = ['user']

admin.site.register(FavoriteLocation, FavoriteLocationAdmin)
