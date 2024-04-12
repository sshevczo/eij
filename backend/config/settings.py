import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'mc)zt@pv_w*ovE9flf#+t638(!y&u&6)4&3^pz#h8y%m&h#')
DEBUG = os.environ.get('DEBUG', 0)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1 localhost .ngrok.io 52.170.250.55').split(' ')
# CSRF_TRUSTED_ORIGINS = ['http://api-dev.eij.org', 'https://api-dev.eij.org']
# SITE_URL = 'https://api-dev.eij.org'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_celery_beat',
    'eij'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

CORS_ALLOW_ALL_ORIGINS = True  # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS = [
#     'http://api-dev.eij.org', 'https://api-dev.eij.org', 'http://20.232.116.40', 'https://eij.org',
#     'http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001',
# ]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('POSTGRES_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('POSTGRES_DB', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('POSTGRES_USER', 'user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}
if DATABASES.get('default').get('ENGINE') != 'django.db.backends.sqlite3':
    DATABASES.get('default').update({'OPTIONS': {'sslmode': 'require'}})

LANGUAGE_CODE = 'en-us'  # 'uk'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = 'static/'
#STATICFILES_DIRS = [
#    BASE_DIR / 'static',
#]
STATIC_ROOT = BASE_DIR / 'static/'
MEDIA_ROOT = BASE_DIR / 'media/'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'eij API docs',
    'DESCRIPTION': 'eij API documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Celery Configuration Options
CELERY_TIMEZONE = "Europe/Kiev"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 60 * 8
REDIS_HOST = "redis"
REDIS_PORT = "6379"
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_BROKER_URL = "redis://" + REDIS_HOST + ":" + REDIS_PORT + "/0"
CELERY_RESULT_BACKEND = "redis://" + REDIS_HOST + ":" + REDIS_PORT + "/0"
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1

AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
AZURE_TRANSLATE_API_KEY = os.environ.get('AZURE_TRANSLATE_API_KEY')

OPENAI_KEY = os.environ.get('OPENAI_KEY')
MAIN_MCC_ID = os.environ.get('MAIN_MCC_ID')

HELICONE_API_KEY = os.environ.get('HELICONE_API_KEY')
