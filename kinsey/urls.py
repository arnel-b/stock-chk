from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('home', views.home, name='home'),
	path('progress', views.progress, name='progress'),
	path('resume', views.resume, name='resume'),
	path('cancelled', views.cancelled, name='cancelled'),
]