from functools import partial

from django.db.models import IntegerField
from django.utils.translation import ugettext_lazy as _

from referral_project.utils.django.enums import IntEnumChoices


class PaymentMethodOption(IntEnumChoices):
    UNKNOWN = -1
    WITHDRAW = 0
    DEPOSIT = 1

    class Labels:
        UNKNOWN = _("Unknown")
        DEPOSIT = _("Deposit")
        WITHDRAW = _("Withdraw")


PaymentMethodOptionField = partial(
    IntegerField,
    choices=PaymentMethodOption.choices(),
    default=PaymentMethodOption.UNKNOWN
)
