from django.shortcuts import render
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from website.models import Post
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'account.register_done.html', {'new_user':new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account.register.html', {'user_form':user_form})

@login_required
def delete(request):
    return render(request, 'account.delete.html')

@login_required
def dashboard(request):
    return render(request, 'account.dashboard.html')

@login_required
def published(request):
    posts = Post.objects.filter(author=request.user, status=Post.Status.PUBLISHED)
    return render(request, 'account.published.html', {
        'posts': posts
    })

@login_required
def drafts(request):
    posts = Post.objects.filter(author=request.user, status=Post.Status.DRAFT)
    return render(request, 'account.drafts.html', {
        'posts': posts
    })

@login_required
def gallery(request):
    return render(request, 'account.gallery.html')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account.profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def notifications(request):
    return render(request, 'account.notifications.html')