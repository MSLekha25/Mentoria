from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('programs/', views.programs, name='programs'),
    path('courses/', views.courses, name='courses'),
    path('contact/', views.contact, name='contact'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    
    # Password Reset URLs
    path('reset_password/', views.reset_password_request, name='reset_password'),
    path('reset_password/<str:uidb64>/<str:token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('reset_password/done/', views.reset_password_done, name='reset_password_done'),
    
    # API endpoints for registration and verification
    path('api/register/', views.register_user, name='register_user'),
]