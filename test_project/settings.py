"""
Django settings for test_project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from pathlib import Path
from typing import Final

from decouple import AutoConfig

# Build paths inside the project like this: BASE_DIR.joinpath('some')
# `pathlib` is better than writing: dirname(dirname(dirname(__file__)))
BASE_DIR = Path(__file__).parent.parent

# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
config = AutoConfig(search_path=BASE_DIR.joinpath('config'))

SECRET_KEY = 'super-secret-test'  # noqa: S105

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ()

AUTH_USER_MODEL = 'users.TenantUser'

# Application definition

TENANT_SCHEMAS = config('USE_DTS', default=False, cast=bool)

SHARED_APPS = (
    'tenant_schemas'
    if TENANT_SCHEMAS
    else 'django_tenants',  # mandatory - django_tenants  -tenant_schemas
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tenant_users.permissions',
    'tenant_users.tenants',
    'test_project.companies',
    'test_project.users',
)

TENANT_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tenant_users.permissions',
)

TENANT_MODEL = 'companies.Company'
if not TENANT_SCHEMAS:
    TENANT_DOMAIN_MODEL = 'companies.Domain'


INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

MIDDLEWARE = (
    'tenant_schemas.middleware.TenantMiddleware'
    if TENANT_SCHEMAS
    else 'django_tenants.middleware.TenantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = ('tenant_users.permissions.backend.UserBackend',)

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


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'tenant_schemas.postgresql_backend'
        if TENANT_SCHEMAS
        else 'django_tenants.postgresql_backend',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DJANGO_DATABASE_HOST'),
        'PORT': config('DJANGO_DATABASE_PORT', cast=int),
        'CONN_MAX_AGE': config('CONN_MAX_AGE', cast=int, default=60),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    },
}


DATABASE_ROUTERS = (
    'tenant_schemas.routers.TenantSyncRouter'
    if TENANT_SCHEMAS
    else 'django_tenants.routers.TenantSyncRouter',
)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


PUBLIC_SCHEMA_NAME = 'public'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

TENANT_USERS_DOMAIN = 'example.com'

SESSION_COOKIE_DOMAIN = '.example.com'


# Constants
CHAR_LENGTH: Final = 80
