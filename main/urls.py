from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path("courses/", views.courses, name='courses'),
    path('contacts/', views.contacts, name='contacts'),
    path('login/', views.login, name='login'),
    # path("about", views.about, name="about"),
    # path("more", views.more, name="more")
]