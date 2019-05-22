from functools import partial

from django.db.models import IntegerField
from django.utils.translation import ugettext_lazy as _

from referral_project.utils.django.enums import IntEnumChoices


class Action(IntEnumChoices):
    UNKNOWN = -1
    DEPOSIT = 0
    REWARD = 1
    TRANSFER = 2
    WITHDRAW = 3
    REFERRAL_BONUS = 4

    class Labels:
        UNKNOWN = _("Unknown")
        DEPOSIT = _("Deposit")
        REWARD = _("Reward")
        TRANSFER = _("Transfer")
        WITHDRAW = _("Withdraw")
        REFERRAL_BONUS = _("Referral Bonus")


ActionField = partial(
    IntegerField,
    choices=Action.choices(),
    default=Action.UNKNOWN
)
