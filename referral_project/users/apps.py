from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UsersConfig(AppConfig):
    name = 'referral_project.users'
    verbose_name = _("Users")

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # noqa
