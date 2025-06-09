from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Exists, Count

from .models import Post, LikedItem
from taggit.models import Tag

def home(request):
    return render(request, 'website.home.html')

def posts(request, tag_slug=None):
    """
    Posts list view:
    - Supports filtering by tag
    - Annotates whether current user liked each post
    - Annotates total likes count per post
    - Paginates results
    - Supports partial load (AJAX infinite scroll)
    """

    # ContentType for Post model
    content_type = ContentType.objects.get_for_model(Post)

    # Subquery: whether current user liked each post
    liked_subquery = LikedItem.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=OuterRef('pk')
    )

    # Base queryset: published posts + annotations
    posts_queryset = Post.published.select_related(
        'author',
        'author__profile'
    ).prefetch_related(
        'tags'
    ).annotate(
        # is_liked: True/False if user liked post
        is_liked=Exists(liked_subquery),
        # likes_count: total number of likes for post
        likes_count=Count('likes')
    ).order_by('-publish')

    # Filter by tag if tag_slug is provided
    current_tag = None
    if tag_slug:
        current_tag = get_object_or_404(Tag, slug=tag_slug)
        posts_queryset = posts_queryset.filter(tags__in=[current_tag])

    # Pagination settings
    page_number = request.GET.get('page', 1)
    list_paginated = request.GET.get('list_paginated', 0)

    posts_paginator = Paginator(posts_queryset, 5)

    try:
        posts_page = posts_paginator.page(page_number)
    except EmptyPage:
        # If infinite scroll: return empty response on overflow
        if list_paginated:
            return HttpResponse('')
    except PageNotAnInteger:
        # Fallback to first page
        posts_page = posts_paginator.page(1)

    # Decide which template to render
    if list_paginated:
        template = 'partials/posts_list.html'
    else:
        template = 'website.posts.html'

    return render(request, template, {
        'posts': posts_page,
        'tag': current_tag
    })

def posts_single(request, year, month, day, slug):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=slug,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # Check if user liked this post
    is_liked = False
    if request.user.is_authenticated:
        content_type = ContentType.objects.get_for_model(Post)
        is_liked = LikedItem.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=post.id
        ).exists()

    # Calculate total likes for this post
    total_likes = LikedItem.objects.filter(
        content_type=content_type,
        object_id=post.id
    ).count()

    return render(request, 'website.posts_single.html', {
        'post': post,
        'is_liked': is_liked,
        'total_likes': total_likes
    })

@login_required
def posts_single_draft(request, slug):
    post = get_object_or_404(
        Post,
        author=request.user,
        slug=slug,
    )
    return render(request, 'website.posts_single.html', {
        'post': post
    })

@login_required
def posts_new(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        status = request.POST.get('action')
        tags = request.POST.get('tags')

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

            if len(tags) > 0:
                post.tags.set([tag.strip() for tag in tags.split(',')])

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

            if len(tags) > 0:
                post.tags.set([tag.strip() for tag in tags.split(',')])

            return JsonResponse({'url': f'/posts/{post.slug}'})
    else:
        tags = Tag.objects.all()
        return render(request, 'website.posts_new.html', {
            'tags': tags
        })

@login_required
def posts_edit(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    if request.method == 'POST':

        post.title = request.POST.get('title')
        post.body = request.POST.get('body')
        tags = request.POST.get('tags')

        post.save()

        if len(tags) == 0:
            post.tags.clear()
        else:            
            post.tags.set([tag.strip() for tag in tags.split(',')])
        
        if  post.status == post.Status.PUBLISHED:
            return JsonResponse({'url': post.get_absolute_url()})
        elif post.status == post.Status.DRAFT:
            return JsonResponse({'url': f'/posts/{post.slug}'})
    
    tags = Tag.objects.all()
    return render(request, 'website.posts_edit.html', {
        'post': post,
        'tags': tags
    })

@login_required
def post_publish(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    post.status = Post.Status.PUBLISHED
    post.publish = timezone.now()
    post.save()
    return redirect(post.get_absolute_url())

@login_required
@require_POST
def like_post(request):
    action = request.POST.get('action')
    post_id = request.POST.get('id')

    content_type = ContentType.objects.get_for_model(Post)

    if action == 'like':
        LikedItem.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=post_id
        )
    else:
        LikedItem.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=post_id
        ).delete()

    return JsonResponse({'action':action})

def about(request):
    return render(request, 'website.about.html')

def search(request):
    return render(request, 'website.search.html')