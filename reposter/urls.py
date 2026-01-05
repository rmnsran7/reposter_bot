"""
URL routes for the reposter app.
"""
from django.urls import path
from . import views

app_name = 'reposter'

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit_url, name='submit'),
    path('cookies/', views.cookies_page, name='cookies'),
    path('cookies/save/', views.save_cookies, name='save_cookies'),
]
