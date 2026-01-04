"""
URL routes for the reposter app.
"""
from django.urls import path
from . import views

app_name = 'reposter'

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit_url, name='submit'),
]
