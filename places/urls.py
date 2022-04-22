from django.contrib import admin
from django.urls import path
from .views import PlacesInCityView

app_name = 'places'

urlpatterns = [
    path('<slug:cityslug>', PlacesInCityView, name='city'),

]