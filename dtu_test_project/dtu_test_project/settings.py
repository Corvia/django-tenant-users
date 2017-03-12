"""
Django settings for dtu_test_project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%-@80c)i9@htvdo#ulmrail^%kizuoddr$(8d6*2r^eczhj#^1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'users.TenantUser'

# Application definition

if os.environ.get('TENANT_APP', 'tenant_schemas') == 'django_tenants':
    TENANT_SCHEMAS = False
else:
    TENANT_SCHEMAS = True

SHARED_APPS = (
    'tenant_schemas' if TENANT_SCHEMAS else 'django_tenants',  # mandatory - django_tenants  -tenant_schemas
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'tenant_users.permissions',
    'tenant_users.tenants',
    'core',
    'customers',
    'users',
)

TENANT_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tenant_users.permissions',
)

TENANT_MODEL = 'customers.Client'
if not TENANT_SCHEMAS:
    TENANT_DOMAIN_MODEL = 'customers.Domain'


INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

MIDDLEWARE_CLASSES = (
    'tenant_schemas.middleware.TenantMiddleware' if TENANT_SCHEMAS else 'django_tenants.middleware.TenantMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'tenant_users.permissions.backend.UserBackend',
)

ROOT_URLCONF = 'dtu_test_project.urls_tenants'
PUBLIC_SCHEMA_URLCONF = 'dtu_test_project.urls_public'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'dtu_test_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'tenant_schemas.postgresql_backend' if TENANT_SCHEMAS else 'django_tenants.postgresql_backend',
        'NAME': os.environ.get('PG_DATABASE', 'dtu_test_project'),
        'USER': os.environ.get('PG_USER', 'postgres'),
        'PASSWORD': os.environ.get('PG_PASSWORD', 'password'),
        'HOST': '127.0.0.1',
    }
}


DATABASE_ROUTERS = (
    'tenant_schemas.routers.TenantSyncRouter' if TENANT_SCHEMAS else 'django_tenants.routers.TenantSyncRouter',
)

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

TENANT_USERS_DOMAIN = "example.com"

SESSION_COOKIE_DOMAIN = '.example.com'
