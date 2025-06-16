from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Exists, Count, Q, Prefetch, Value, BooleanField

from .models import Post, LikedItem, Comment, Reply, Bookmark
from .forms import CommentForm, ReplyForm
from taggit.models import Tag

def home(request):
    return render(request, 'website.home.html')

def posts(request, tag_slug=None):
    """
    Posts list view:
    - Supports filtering by tag
    - Annotates whether current user liked/bookmarked each post (if authenticated)
    - Annotates total likes and comment count
    - Paginates results
    - Supports partial load (AJAX infinite scroll)
    """

    # Base queryset
    posts_queryset = Post.published.select_related(
        'author',
        'author__profile'
    ).prefetch_related(
        'tags'
    )

    # ContentType for Post model
    content_type = ContentType.objects.get_for_model(Post)

    if request.user.is_authenticated:
        # Subquery: liked posts
        liked_subquery = LikedItem.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=OuterRef('pk')
        )

        # Subquery: bookmarked posts
        bookmark_subquery = Bookmark.objects.filter(
            user=request.user,
            post=OuterRef('pk')
        )

        posts_queryset = posts_queryset.annotate(
            is_liked=Exists(liked_subquery),
            is_bookmarked=Exists(bookmark_subquery)
        )
    else:
        # Anonymous users: mark as False
        posts_queryset = posts_queryset.annotate(
            is_liked=Value(False, output_field=BooleanField()),
            is_bookmarked=Value(False, output_field=BooleanField())
        )

    # Add common annotations
    posts_queryset = posts_queryset.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', filter=Q(comments__active=True), distinct=True),
        bookmarks_count=Count('bookmarks', distinct=True)
    ).order_by('-publish')

    # Filter by tag if applicable
    current_tag = None
    if tag_slug:
        current_tag = get_object_or_404(Tag, slug=tag_slug)
        posts_queryset = posts_queryset.filter(tags__in=[current_tag])

    # Pagination
    page_number = request.GET.get('page', 1)
    list_paginated = request.GET.get('list_paginated', 0)
    paginator = Paginator(posts_queryset, 5)

    try:
        posts_page = paginator.page(page_number)
    except EmptyPage:
        return HttpResponse('') if list_paginated else paginator.page(1)
    except PageNotAnInteger:
        posts_page = paginator.page(1)

    # Template
    template = 'partials/posts_list.html' if list_paginated else 'website.posts.html'

    return render(request, template, {
        'posts': posts_page,
        'tag': current_tag
    })

def posts_single(request, year, month, day, slug):
    # Get the post
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=slug,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    is_liked_post = False
    is_bookmarked = False
    liked_comment_ids = set()
    liked_reply_ids = set()
    post_ct = ContentType.objects.get_for_model(Post)

    if request.user.is_authenticated:
        # Check if user bookmarked the post
        is_bookmarked = Bookmark.objects.filter(
            user=request.user,
            post=post
        ).exists()

        # Check if user liked the post
        is_liked_post = LikedItem.objects.filter(
            user=request.user,
            content_type=post_ct,
            object_id=post.id
        ).exists()

        # Check liked comments for the authed user
        comment_ct = ContentType.objects.get_for_model(Comment)
        comment_ids = post.comments.values_list('id', flat=True)
        liked_comment_ids = set(
            LikedItem.objects.filter(
                user=request.user,
                content_type=comment_ct,
                object_id__in=comment_ids
            ).values_list('object_id', flat=True)
        )

        # Check liked replies for the authed user
        reply_ct = ContentType.objects.get_for_model(Reply)
        reply_ids = Reply.objects.filter(comment__post=post).values_list('id', flat=True)
        liked_reply_ids = set(
            LikedItem.objects.filter(
                user=request.user,
                content_type=reply_ct,
                object_id__in=reply_ids
            ).values_list('object_id', flat=True)
        )

    # Calculate total likes for this post
    total_likes = LikedItem.objects.filter(
        content_type=post_ct,
        object_id=post.id
    ).count()

    # Calculate total bookmarks
    total_bookmarks = post.bookmarks.count()

    # Load active comments related to this post with their replies
    reply_qs = Reply.objects.select_related(
        'author', 'author__profile'
    ).annotate(
        likes_count=Count('likes', distinct=True)
    )
    comments = post.comments.order_by(
        '-created'
    ).select_related(
        'author', 'author__profile'
    ).prefetch_related(
        Prefetch(
            'replies', 
            queryset=reply_qs)
    ).annotate(
        likes_count=Count('likes', distinct=True),
        replies_count=Count('replies', filter=Q(replies__active=True), distinct=True)
    )

    # Count comments and replies
    totals = post.comments.filter(
        active=True
    ).aggregate(
        total_comments=Count('id', distinct=True),
        total_replies=Count('replies', filter=Q(replies__active=True))
    )

    return render(request, 'website.posts_single.html', {
        'post': post,
        'is_liked_post': is_liked_post,
        'is_bookmarked': is_bookmarked,
        'total_likes': total_likes,
        'total_comments_replies': totals['total_comments'] + totals['total_replies'],
        'total_bookmarks': total_bookmarks,
        'comments': comments,
        'liked_comment_ids': liked_comment_ids,
        'liked_reply_ids': liked_reply_ids
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
def like_post(request, id):
    action = request.POST.get('action')

    content_type = ContentType.objects.get_for_model(Post)

    if action == 'like':
        LikedItem.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=id
        )
    else:
        LikedItem.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=id
        ).delete()

    return JsonResponse({'action':action})

@login_required
@require_POST
def comment_on_post(request, id):
    post = get_object_or_404(
        Post,
        id=id,
        status=Post.Status.PUBLISHED
    )
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect(f'{post.get_absolute_url()}#comment-{comment.id}')

@login_required
@require_POST
def reply_on_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id
    )
    form = ReplyForm(data=request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.comment = comment
        reply.author = request.user
        reply.save()
        return redirect(f'{comment.post.get_absolute_url()}#reply-{reply.id}')
    else:
        return redirect(comment.post.get_absolute_url())

@login_required
@require_POST
def update_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id
    )
    form = CommentForm(request.POST, instance=comment)
    if form.is_valid():
        form.save()
    return redirect(f'{comment.post.get_absolute_url()}#comment-{comment.id}')

@login_required
@require_POST
def active_comment(request, post_id, comment_id):
    print('active_comment')
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id
    )
    comment.active = request.POST.get('active') == 'true'
    comment.save()
    return redirect(f'{comment.post.get_absolute_url()}#comment-{comment.id}')

@login_required
@require_POST
def update_reply(request, comment_id, reply_id):
    reply = get_object_or_404(
        Reply,
        id=reply_id,
        comment_id=comment_id
    )
    form = ReplyForm(request.POST, instance=reply)
    if form.is_valid():
        form.save()
    return redirect(f'{reply.comment.post.get_absolute_url()}#reply-{reply.id}')

@login_required
@require_POST
def active_reply(request, comment_id, reply_id):
    print('active_reply')
    reply = get_object_or_404(
        Reply,
        id=reply_id,
        comment_id=comment_id
    )
    reply.active = request.POST.get('active') == 'true'
    reply.save()
    return redirect(f'{reply.comment.post.get_absolute_url()}#reply-{reply.id}')

@login_required
@require_POST
def like_comment(request):
    action = request.POST.get('action')
    comment_id = request.POST.get('id')

    content_type = ContentType.objects.get_for_model(Comment)

    if action == 'like':
        LikedItem.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=comment_id
        )
    else:
        LikedItem.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=comment_id
        ).delete()

    return JsonResponse({'action':action})

@login_required
@require_POST
def like_reply(request):
    action = request.POST.get('action')
    reply_id = request.POST.get('id')

    content_type = ContentType.objects.get_for_model(Reply)

    if action == 'like':
        LikedItem.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=reply_id
        )
    else:
        LikedItem.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=reply_id
        ).delete()

    return JsonResponse({'action':action})

@login_required
@require_POST
def bookmark_post(request, id):
    action = request.POST.get('action')

    post = get_object_or_404(
        Post,
        id=id,
        status=Post.Status.PUBLISHED
    )

    if action == 'bookmark':
        Bookmark.objects.get_or_create(
            post=post,
            user=request.user
        )
    else:
        Bookmark.objects.filter(
            post=post,
            user=request.user
        ).delete()

    return JsonResponse({'action': action})

def about(request):
    return render(request, 'website.about.html')

def search(request):
    return render(request, 'website.search.html')