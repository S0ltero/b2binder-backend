import os
from os.path import join
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third party apps
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",

    # Local apps
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = int(os.environ.get("DJANGO_DEBUG", default=0))
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# General
APPEND_SLASH = True
LANGUAGE_CODE = "ru"
LOGIN_REDIRECT_URL = "/"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
USE_L10N = True

USE_TZ = True
TIME_ZONE = "Europe/Moscow"

#Cors
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# Postgres
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

AUTH_USER_MODEL = 'api.CustomUser'

# Djoser settings
DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SEND_CONFIRMATION_EMAIL": False,
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "user": "api.serializers.UserSerializer",
        "user_create": "api.serializers.UserCreateSerializer",
        "user_create_password_retype": "api.serializers.UserCreateSerializer",
        "current_user": "api.serializers.UserSerializer",
        "token": "api.serializers.TokenSerializer"
    },

}

# RestFramework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = join(os.path.dirname(BASE_DIR), "static")
STATICFILES_DIRS = []
STATIC_URL = "/static/"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Media files
MEDIA_ROOT = join(os.path.dirname(BASE_DIR), "media")
MEDIA_URL = "/media/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
