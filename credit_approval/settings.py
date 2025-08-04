from pathlib import Path
import dj_database_url
import os
from dotenv import load_dotenv
import environ

# Initialize environment variables handler
env = environ.Env()
environ.Env.read_env()

# Define base project directory path
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Secure key used by Django for cryptographic operations
SECRET_KEY = os.getenv('SECRET_KEY')

# Toggle debug mode based on environment config
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# Allowed hostnames that can access the app
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

# Installed apps for admin, API, docs, and custom app
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',     # For building REST APIs
    'core',               # Your app that handles core logic
    'drf_yasg',           # Swagger UI for API documentation
]

# Middleware stack for request/response processing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Main routing configuration for URL handling
ROOT_URLCONF = 'credit_approval.urls'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Template engine configuration for rendering HTML pages
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI entry point for production servers
WSGI_APPLICATION = 'credit_approval.wsgi.application'

# PostgreSQL database configuration pulled from environment
DATABASES = {
    'default': dj_database_url.parse(os.getenv('SAI_DB'))
}

# Validators for password strength and user safety
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Language and timezone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# URL for accessing static files (e.g. CSS, JS)
STATIC_URL = 'static/'

# Default ID field type for auto-generated primary keys
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
