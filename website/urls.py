from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.posts, name='posts'),
    path('posts/<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_single, name='post_single'),
    path('posts/<slug:slug>/', views.post_single_draft, name='post_single_draft'),
    path('posts/<int:id>/publish/', views.post_publish, name='post_publish'),
    path('posts/<int:id>/edit/', views.posts_edit, name='post_edit'),
    path('posts/new', views.posts_new, name='posts_new'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
]