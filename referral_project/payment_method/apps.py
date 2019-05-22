from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PaymentMethodsConfig(AppConfig):
    name = 'referral_project.payment_method'
    verbose_name = _("PaymentMethod")

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # noqa
