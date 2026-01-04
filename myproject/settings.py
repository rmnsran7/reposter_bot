"""
Django settings for InstaReposter project.
"""
from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='reposter-bot-secret-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']  # Update for production

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'reposter',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
        ],
    },
}]

WSGI_APPLICATION = 'myproject.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = '/static/'

# Media files (for temporary downloads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 600  # 10 minutes max per task

# Meta/Instagram API Configuration
IG_BUSINESS_ID = config('IG_BUSINESS_ACCOUNT_ID')
ACCESS_TOKEN = config('IG_PAGE_ACCESS_TOKEN')
GRAPH_VERSION = 'v21.0'

# ngrok URL for local development (update when starting ngrok)
NGROK_URL = config('NGROK_URL', default='')

# Custom caption appended to every post
CUSTOM_CAPTION = "#surreybc #newtonsurrey #surreycentral #strawberryhill #punjabiincanada #surreypind #internationalstudents #kpu #gediroute #surreylife #surreywale"