from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path("courses/", views.courses, name='courses'),
    path('contacts/', views.contacts, name='contacts'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('materials/', views.materials, name='materials'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('verify/<uuid:code>/', views.verify_email, name='verify_email'),
    path('email-sent/', views.email_sent, name='email_sent'),
    # path("about", views.about, name="about"),
    # path("more", views.more, name="more")
]