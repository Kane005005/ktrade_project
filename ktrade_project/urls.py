# ktrade_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as marketplace_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # ALLAUTH EN PREMIER (important)
    path('accounts/', include('accounts.urls')),  # Vos URLs personnalisées après
    path('marketplace/', include('marketplace.urls')),
    path('chat/', include('chat.urls')),
    path('', marketplace_views.home, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)