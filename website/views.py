from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify

from .models import Post

def home(request):
    return render(request, 'website.home.html')

def posts(request):
    posts = Post.published.all()
    return render(request, 'website.posts.html', {
        'posts': posts
    })

def post_single(request, year, month, day, slug):
    if request.resolver_match.url_name == 'collection_post_single':
        post = get_object_or_404(
            Post,
            author=request.user,
            slug=slug,
            publish__year=year,
            publish__month=month,
            publish__day=day,
        )
    elif request.resolver_match.url_name == 'post_single':
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
    title = request.POST.get('title')
    body = request.POST.get('body')
    status = Post.Status.PUBLISHED if request.POST.get('action') == Post.Status.PUBLISHED else Post.Status.DRAFT
    if request.method == 'POST':
        post = Post(
            title=title,
            slug=slugify(title),
            body=body,
            status=status,
            author=request.user
        )
        post.save()
        if status == Post.Status.PUBLISHED:
            return JsonResponse({'url': post.get_absolute_url()})
        elif status == Post.Status.DRAFT:
            return JsonResponse({'url': f'/collection{post.get_absolute_url()}'})
    return render(request, 'website.posts_new.html')

@login_required
def collection_post_edit(request):
    return render(request, 'website.collection_post_edit.html')

def about(request):
    return render(request, 'website.about.html')

def search(request):
    return render(request, 'website.search.html')