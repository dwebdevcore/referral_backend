from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TransactionsConfig(AppConfig):
    name = 'referral_project.transactions'
    verbose_name = _("Transactions")

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # noqa
