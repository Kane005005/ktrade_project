# ktrade_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as marketplace_views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Vos URLs personnalisées AVANT allauth
    path('accounts/login/', accounts_views.custom_login, name='custom-login'),
    path('accounts/register/', accounts_views.register, name='register'),
    path('accounts/logout/', accounts_views.custom_logout, name='custom-logout'),
    
    # Allauth (pour la gestion sociale et autres)
    path('accounts/', include('allauth.urls')),
    
    # Vos autres URLs
    path('accounts/', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('chat/', include('chat.urls')),
    path('', marketplace_views.home, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)