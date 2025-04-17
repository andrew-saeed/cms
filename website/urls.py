from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home),
    path('posts/', views.posts),
    path('about/', views.about),
]