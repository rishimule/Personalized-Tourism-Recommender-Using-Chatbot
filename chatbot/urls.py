from django.contrib import admin
from django.urls import path
from .views import indexView, FromChatbotView

app_name = 'chatbot'

urlpatterns = [
    path('', indexView, name='index'),
    path('recommend', FromChatbotView, name='from_chatbot'),
]