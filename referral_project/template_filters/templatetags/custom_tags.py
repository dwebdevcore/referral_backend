import os

from django import template

register = template.Library()


@register.inclusion_tag('tags/include_raven.html')
def include_raven(scheme=None):
    if os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings.production':
        from raven.contrib.django.models import client
        sentry_public_dsn = client.get_public_dsn(scheme)
    else:
        sentry_public_dsn = None

    return {
        'sentry_public_dsn': sentry_public_dsn
    }


@register.simple_tag
def is_production():
    return os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings.production'

@register.simple_tag
def is_local():
    return os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings.local'


@register.simple_tag
def get_host(request):
    return request.get_host().rsplit(":", 1)[0]
