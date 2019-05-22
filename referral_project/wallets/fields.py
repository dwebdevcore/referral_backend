from functools import partial

from django.db.models import IntegerField
from django.utils.translation import ugettext_lazy as _

from referral_project.utils.django.enums import IntEnumChoices


class WalletKind(IntEnumChoices):
    """
    EXTERNAL:
        a "real-world" wallet
        for fiat deposits/withdrawals.
    """
    MAIN = 0
    TRANSFER = 1
    REFERRAL = 2
    EXTERNAL = 3

    class Labels:
        MAIN = _('Main')
        TRANSFER = _('Transfer')
        REFERRAL = _('Referral')
        EXTERNAL = _('External')


WalletKindField = partial(
    IntegerField,
    choices=WalletKind.choices(),
    default=WalletKind.MAIN,
)
