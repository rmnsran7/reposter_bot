from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'reposter-bot-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*'] # Change to your domain in production

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'reposter',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'bot_project.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
}]

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

# Media Storage
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Celery
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Meta Credentials
IG_BUSINESS_ID = config('IG_BUSINESS_ACCOUNT_ID')
ACCESS_TOKEN = config('IG_PAGE_ACCESS_TOKEN')
GRAPH_VERSION = 'v24.0'