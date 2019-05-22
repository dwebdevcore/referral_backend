from django.utils.translation import ugettext_lazy as _

from referral_project.utils.django.enums import StrEnumChoices


class GroupName(StrEnumChoices):
    REGULAR = "Regular"
    REGIONAL = "Regional"
    SUPER = "Super"
    SYSTEM = "System"

    class Labels:
        REGULAR = _("Regular")
        REGIONAL = _("Regional")
        SUPER = _("Super")
        SYSTEM = _("System")
