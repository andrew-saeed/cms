from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'website.home.html')

def posts(request):
    return render(request, 'website.posts.html')

@login_required
def posts_new(request):
    return render(request, 'website.posts_new.html')

def about(request):
    return render(request, 'website.about.html')

def search(request):
    return render(request, 'website.search.html')