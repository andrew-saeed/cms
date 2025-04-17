from django.shortcuts import render

def home(request):
    return render(request, 'website.home.html')

def posts(request):
    return render(request, 'website.posts.html')

def about(request):
    return render(request, 'website.about.html')