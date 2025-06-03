from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('published/', views.published, name='published'),
    path('drafts/', views.drafts, name='drafts'),
    path('gallery/', views.gallery, name='gallery'),
    path('profile/', views.profile, name='profile'),
    path('delete-account/', views.delete, name='delete'),
    path('notifications/', views.notifications, name='notifications'),
]