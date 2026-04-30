
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile-update'),
    path('profile/<int:user_id>/', views.public_profile, name='public-profile'),
    path('login/', views.custom_login, name='custom-login'),
    path('profile/api/update/', views.profile_update_api, name='profile-update-api'), 
    path('logout/', views.custom_logout, name='custom-logout'),
    path('change-password/', views.change_password, name='change-password'),
]