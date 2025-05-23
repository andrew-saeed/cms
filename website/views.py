from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.utils import timezone

from .models import Post

def home(request):
    return render(request, 'website.home.html')

def posts(request):
    posts = Post.published.all()
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
def post_single_draft(request, slug):
    post = get_object_or_404(
        Post,
        author=request.user,
        slug=slug,
    )
    return render(request, 'website.post_single.html', {
        'post': post
    })

@login_required
def posts_new(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        status = request.POST.get('action')
        if status == Post.Status.PUBLISHED:
            post = Post(
                title=title,
                slug=slugify(title),
                body=body,
                status=status,
                author=request.user,
                publish=timezone.now()
            )
            post.save()
            return JsonResponse({'url': post.get_absolute_url()})
        elif status == Post.Status.DRAFT:
            post = Post(
                title=title,
                slug=slugify(title),
                body=body,
                status=status,
                author=request.user,
            )
            post.save()
            return JsonResponse({'url': f'/posts/{post.slug}'})
    return render(request, 'website.posts_new.html')

@login_required
def posts_edit(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.body = request.POST.get('body')
        post.save()
        if  post.status == post.Status.PUBLISHED:
            return JsonResponse({'url': post.get_absolute_url()})
        elif post.status == post.Status.DRAFT:
            return JsonResponse({'url': f'/posts/{post.slug}'})
    return render(request, 'website.posts_edit.html', {
        'post': post
    })

@login_required
def post_publish(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    post.status = Post.Status.PUBLISHED
    post.publish = timezone.now()
    post.save()
    return redirect(post.get_absolute_url())

def about(request):
    return render(request, 'website.about.html')

def search(request):
    return render(request, 'website.search.html')