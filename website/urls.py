from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.posts, name='posts'),
    path('posts/new', views.posts_new, name='posts_new'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
]