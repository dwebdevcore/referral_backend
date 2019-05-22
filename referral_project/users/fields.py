from functools import partial

from django.db.models import IntegerField
from django.utils.translation import ugettext_lazy as _

from referral_project.utils.django.enums import IntEnumChoices


class ActivatedDeactivatedStatus(IntEnumChoices):
    DEACTIVATED = 0
    ACTIVATED = 1

    class Labels:
        DEACTIVATED = _("Deactivated")
        ACTIVATED = _("Activated")


ActivatedDeactivatedStatusField = partial(
    IntegerField,
    choices=ActivatedDeactivatedStatus.choices(),
    default=ActivatedDeactivatedStatus.DEACTIVATED,
)

class IDKind(IntEnumChoices):
    PASSPORT = 0
    GOVERNMENT_ID = 1
    DIVING_LICENSE = 2

    class Labels:
        PASSPORT = _("Passport")
        GOVERNMENT_ID = _("Government ID")
        DIVING_LICENSE = _("Diving License")


IDKindField = partial(
    IntegerField,
    choices=IDKind.choices(),
    default=IDKind.PASSPORT,
)
