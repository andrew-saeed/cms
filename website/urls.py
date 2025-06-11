from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.posts, name='posts'),
    path('posts/new/', views.posts_new, name='posts_new'),
    path('posts/like_post/', views.like_post, name='like_post'),
    path('posts/tag/<slug:tag_slug>', views.posts, name='posts_by_tag'),
    path('posts/<int:year>/<int:month>/<int:day>/<slug:slug>/', views.posts_single, name='posts_single'),
    path('posts/<slug:slug>/', views.posts_single_draft, name='posts_single_draft'),
    path('posts/<int:id>/publish/', views.post_publish, name='post_publish'),
    path('posts/<int:id>/edit/', views.posts_edit, name='post_edit'),
    path('posts/<int:id>/comments/', views.comment_on_post, name='comment_on_post'),
    path('posts/<int:post_id>/comments/<int:comment_id>', views.reply_on_comment, name='reply_on_comment'),
    path('posts/<int:post_id>/comments/<int:comment_id>/update', views.update_comment, name='update_comment'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
]