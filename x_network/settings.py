"""
Django settings for x_network project.
Generated by 'django-admin startproject' using Django 2.2.
For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import djcelery
from celery.schedules import crontab, timedelta
from kombu import Exchange, Queue
from .celery import app

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(r(zxi)ta$ie-ci8e_jwa)k#kn^p-ze942q5@hvyf6n=gd_+^-'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方包
    'rest_framework',
    'xadmin',
    'crispy_forms',
    'reversion',
    'celery',
    'djcelery',
    # 'stdimage' # 图片字段
    # 子应用
    'network',
    'corsheaders'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'x_network.my_middleware.LoginMiddleware'
]

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'x_network.urls'

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

WSGI_APPLICATION = 'x_network.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rosdb',
        'USER': 'pgros',
        'PASSWORD': 'rosrouter',
        'HOST': '172.17.0.11',
        # 'NAME': 'ros',
        # 'USER': 'yyy',
        # 'PASSWORD': 'yyy.1234',
        # 'HOST': '118.190.88.165',
        'PORT': 5432,
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(SITE_ROOT, 'collectedstatic')

# celery


djcelery.setup_loader()
BROKER_URL = 'amqp://admin:ros@localhost:5672//'
CELERY_RESULT_BACKEND = 'redis://:ros@localhost/1'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = ('network.tasks')
CELERY_TIMEZONE = 'Asia/Shanghai'

app.conf.task_routes = {
    'tasks.l2tp_vpn_scan': {'queue': 'l2tp_vpn_scan'},
    'tasks.traffic': {'queue': 'traffic'}
}
CELERYBEAT_SCHEDULE = {
    'l2tp_vpn_scan': {
        "task": "network.tasks.l2tp_vpn_scan",
        "schedule": timedelta(hours=1),
        "args": ()
    },
    'traffic': {
        "task": "network.tasks.master_traffic",
        "schedule": timedelta(hours=1),
        "args": ()
    },
}

# logging


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(pathname)s:%(lineno)s %(process)d %(thread)d %(message)s"
        },
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
    },
    "filters": {},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": [],
            "class": "logging.StreamHandler",
            "formatter": "verbose"
        },
        "default": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/x_network.log",
            "maxBytes": 1024 * 1024 * 50,  # 50M
            "backupCount": 2,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": [],
        },
        # "syslog": {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.SysLogHandler',
        #     'formatter': 'simple',
        #     'facility': 'local4',
        #     'address': '/dev/log',
        # },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "default"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console", "default"],
            "level": "ERROR",
            "propagate": False,
        },
        "network": {
            "handlers": ["console", "default"],
            "level": "INFO",
            "filters": []
        },
        # "rsyslog": {
        #     "handlers": ["syslog", ],
        #     "level": "INFO",
        #     'propagate': True,
        # }

    }
}

# Redis缓存
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis:localhost:6379',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "ros",
        },
    },
}

# ZABBIX API
ZABBIX_URL = 'http://122.51.39.93/zabbix/api_jsonrpc.php'
ZABBIX_HEADER = {"Content-Type": "application/json"}
TEST = 123

try:
    # 会导入debug_setting里全部参数，遇到一样的参数就会覆盖 就像 a =1，a=2 最终a的值是2
    from x_network.debug_settings import *
except ModuleNotFoundError:
    pass
