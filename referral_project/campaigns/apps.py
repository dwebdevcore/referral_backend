from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CampaignsConfig(AppConfig):
    name = 'referral_project.campaigns'
    verbose_name = _("Campaigns")

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # noqa
