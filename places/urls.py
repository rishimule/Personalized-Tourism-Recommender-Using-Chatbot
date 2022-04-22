from django.contrib import admin
from django.urls import path
from .views import PlacesInCityView, SearchHistoryView

app_name = 'places'

urlpatterns = [
    path('history/show/',SearchHistoryView, name='history'),
    path('<slug:cityslug>', PlacesInCityView, name='city'),

]