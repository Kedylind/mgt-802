"""
Django settings for case_interview_simulator project.
"""
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

# Get allowed hosts from environment, or use Railway's default domain
# Handle both comma-separated string and list format
allowed_hosts_str = env('ALLOWED_HOSTS', default='')
if allowed_hosts_str:
    # Split by comma if it's a string, otherwise use as-is
    if isinstance(allowed_hosts_str, str):
        ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]
    else:
        ALLOWED_HOSTS = allowed_hosts_str if isinstance(allowed_hosts_str, list) else [allowed_hosts_str]
else:
    ALLOWED_HOSTS = []

if not ALLOWED_HOSTS:
    # Railway provides RAILWAY_PUBLIC_DOMAIN, fallback to common defaults
    railway_domain = env('RAILWAY_PUBLIC_DOMAIN', default=None)
    if railway_domain:
        # Extract base domain (remove protocol if present)
        base_domain = railway_domain.replace('https://', '').replace('http://', '').split('/')[0]
        ALLOWED_HOSTS = [base_domain]
    else:
        ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Add Railway domain if present
railway_domain = env('RAILWAY_PUBLIC_DOMAIN', default=None)
if railway_domain:
    if not railway_domain.startswith('http'):
        railway_domain = f'https://{railway_domain}'
    CSRF_TRUSTED_ORIGINS.append(railway_domain)

# Application definition
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'accounts',
    'interviews',
    'cases',
    'agents',
    'analysis',
    'feedback',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'case_interview_simulator.urls'

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

WSGI_APPLICATION = 'case_interview_simulator.wsgi.application'
ASGI_APPLICATION = 'case_interview_simulator.asgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Use SQLite for local development if DATABASE_URL is not set
if env('DATABASE_URL', default=None):
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (user uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Login/Logout URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Channels configuration (for WebSockets)
# Use in-memory channel layer for local development if Redis is not available
REDIS_URL = env('REDIS_URL', default=None)
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [REDIS_URL],
            },
        },
    }
else:
    # Fallback to in-memory channel layer for local development
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# API Keys (from environment variables)
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')
ASSEMBLYAI_API_KEY = env('ASSEMBLYAI_API_KEY', default='')
PINECONE_API_KEY = env('PINECONE_API_KEY', default='')
PINECONE_ENVIRONMENT = env('PINECONE_ENVIRONMENT', default='')
PINECONE_INDEX_NAME = env('PINECONE_INDEX_NAME', default='case-interviews')

# Security settings for production
if not DEBUG:
    # Railway handles SSL termination at the proxy level
    # Trust the X-Forwarded-Proto header from Railway's proxy
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Don't force SSL redirect - Railway already handles this
    SECURE_SSL_REDIRECT = False
    # Still use secure cookies since Railway serves over HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

