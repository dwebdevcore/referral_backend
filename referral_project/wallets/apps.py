from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WalletsConfig(AppConfig):
    name = 'referral_project.wallets'
    verbose_name = _("Wallets")

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # noqa
