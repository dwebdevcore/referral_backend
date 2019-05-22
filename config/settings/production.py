# -*- coding: utf-8 -*-
"""
Production Configurations

- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis for cache

- Use sentry for error logging


"""
from __future__ import absolute_import, unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils import six


from .common import *  # noqa

# read production environment.

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DJANGO_DEBUG', default=False)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

USE_LOG = DEBUG


# raven sentry client
# See https://docs.getsentry.com/hosted/clients/python/integrations/django/
INSTALLED_APPS += ('raven.contrib.django.raven_compat', )
RAVEN_MIDDLEWARE = ('raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
                    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware')
MIDDLEWARE_CLASSES = RAVEN_MIDDLEWARE + MIDDLEWARE_CLASSES


# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['127.0.0.1', '0.0.0.0'])
# END SITE CONFIGURATION

INSTALLED_APPS += ('gunicorn', )


# MailGun settings
# ------------------------------------------------------------------------------
# See https://anymail.readthedocs.io/en/stable/quickstart/
INSTALLED_APPS += ('anymail', )
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"  # or sendgrid.EmailBackend, or...
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL', default="you@example.com")
ANYMAIL_MAILGUN_API_KEY = env('DJANGO_MAILGUN_API_KEY')
if ANYMAIL_MAILGUN_API_KEY is None or not ANYMAIL_MAILGUN_API_KEY:
    raise ImproperlyConfigured('MAILGUN_API_KEY is required.')


# Sentry Configuration
# ---------------------
SENTRY_DSN = env('DJANGO_SENTRY_DSN')
RAVEN_CONFIG = {
    'DSN': SENTRY_DSN
}

# Loggly configuration
# ---------------------
LOGGLY_TOKEN = env('LOGGLY_TOKEN')
if LOGGLY_TOKEN is None or not LOGGLY_TOKEN:
    raise ImproperlyConfigured('Loggly token is required.')

LOGGLY_URL = 'https://logs-01.loggly.com/inputs/%s/tag/python' % LOGGLY_TOKEN

# Logging
# ---------------------
LOGGING['root'] = {
    'level': 'WARNING',
    'handlers': ['sentry'],
}

LOGGING['formatters'].update({
    'json': {
        'format': '{ "loggerName":"%(name)s", "asciTime":"%(asctime)s", "fileName":"%(filename)s",'
                  '"logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s",'
                  '"lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}'
    },
})

LOGGING['handlers'].update({
    'sentry': {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    },
    'loggly': {
        'level': 'INFO',
        'class': 'loggly.handlers.HTTPSHandler',
        'formatter': 'json',
        'url': LOGGLY_URL
    },
})

LOGGING['loggers'].update({
    'django.db.backends': {
        'level': 'ERROR',
        'handlers': ['console'],
        'propagate': False,
    },
    'raven': {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': False,
    },
    'referral_project': {
        'level': 'DEBUG',
        'handlers': ['console', 'loggly', 'sentry'],
        'propagate': False,
    },
    'sentry.errors': {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': False,
    },
    'django.security.DisallowedHost': {
        'level': 'ERROR',
        'handlers': ['console', 'sentry'],
        'propagate': False,
    },
})

# Your production stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
