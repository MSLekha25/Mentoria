from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('programs/', views.programs, name='programs'),
    path('contact/', views.contact, name='contact'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    
    # API endpoints for registration and verification
    path('api/register/', views.register_user, name='register_user'),
]