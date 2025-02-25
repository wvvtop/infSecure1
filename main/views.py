from django.shortcuts import render

def home(request):
    return render(request, "main/home.html")

def about(request):
    return render(request, "main/about.html")

def courses(request):
    return render(request, "main/courses.html")

def contacts(request):
    return render(request, "main/contacts.html")

def login(request):
    return render(request, "main/login.html")

# Create your views here.
