import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-dev')

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'urls_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RequestLoggingMiddleware',
    'core.middleware.GlobalExceptionHandlerMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_db.sqlite3',
        },
        'shard_1': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_shard_1.sqlite3',
        },
        'shard_2': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_shard_2.sqlite3',
        },
        'shard_3': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_shard_3.sqlite3',
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
        'shard_1': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME_SHARD1', 'shard_1'),
            'USER': os.getenv('DB_USER', 'shortener_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'secret_postgres_pass'),
            'HOST': os.getenv('DB_HOST_SHARD1', 'localhost'),
            'PORT': os.getenv('DB_PORT_SHARD1', '5433'),
        },
        'shard_2': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME_SHARD2', 'shard_2'),
            'USER': os.getenv('DB_USER', 'shortener_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'secret_postgres_pass'),
            'HOST': os.getenv('DB_HOST_SHARD2', 'localhost'),
            'PORT': os.getenv('DB_PORT_SHARD2', '5434'),
        },
        'shard_3': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME_SHARD3', 'shard_3'),
            'USER': os.getenv('DB_USER', 'shortener_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'secret_postgres_pass'),
            'HOST': os.getenv('DB_HOST_SHARD3', 'localhost'),
            'PORT': os.getenv('DB_PORT_SHARD3', '5435'),
        },
    }

DATABASE_ROUTERS = ['core.shard_router.ShardRouter']

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

if 'test' in sys.argv:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
