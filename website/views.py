from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Post

def home(request):
    return render(request, 'website.home.html')

def posts(request):
    posts = Post.objects.all()
    return render(request, 'website.posts.html', {
        'posts': posts
    })

def post_single(request, year, month, day, slug):
    post = get_object_or_404(
        Post, 
        status=Post.Status.PUBLISHED,
        slug=slug,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    return render(request, 'website.post_single.html', {
        'post': post
    })

@login_required
def posts_new(request):
    return render(request, 'website.posts_new.html')

def about(request):
    return render(request, 'website.about.html')

def search(request):
    return render(request, 'website.search.html')