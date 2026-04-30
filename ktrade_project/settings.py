# ktrade_project/settings.py
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-votre-clé-secrète-ici')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']  # À restreindre en production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Requis pour allauth
    
    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # Nos apps
    'accounts.apps.AccountsConfig',  # Utilisez le chemin complet
    'marketplace',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Important pour allauth
]

ROOT_URLCONF = 'ktrade_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Requis pour allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ktrade_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Pour la production

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sites framework
SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Backend par défaut
    'allauth.account.auth_backends.AuthenticationBackend',  # Backend allauth
]

# Configuration de django-allauth
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Mettre 'mandatory' en production
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USERNAME_MIN_LENGTH = 3

# Redirection après connexion
LOGIN_REDIRECT_URL = '/'  # Sera overridé par l'adapter
LOGIN_URL = '/accounts/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True  # Déconnexion sans confirmation

# Adapter personnalisé
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'

# Configuration des providers sociaux
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_SECRET', default=''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
            'openid',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account',  # Force la sélection de compte
        },
        'OAUTH_PKCE_ENABLED': True,
        'FETCH_USERINFO': True,  # Récupère les informations utilisateur
        'VERIFIED_EMAIL': True,  # Considère l'email comme vérifié
    }
}

# Paramètres de session
SESSION_COOKIE_AGE = 1209600  # 2 semaines en secondes
SESSION_SAVE_EVERY_REQUEST = True

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# ktrade_project/settings.py

# Formulaire personnalisé pour l'inscription sociale
SOCIALACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSocialSignupForm',
}

# Désactiver l'inscription automatique (pour forcer le formulaire)
SOCIALACCOUNT_AUTO_SIGNUP = False

# Demander l'email obligatoirement
SOCIALACCOUNT_EMAIL_REQUIRED = True# ktrade_project/settings.py

# Formulaire personnalisé pour l'inscription sociale
SOCIALACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSocialSignupForm',
}

# Désactiver l'inscription automatique (pour forcer le formulaire)
SOCIALACCOUNT_AUTO_SIGNUP = False

# Demander l'email obligatoirement
SOCIALACCOUNT_EMAIL_REQUIRED = True