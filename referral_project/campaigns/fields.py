from functools import partial

from django.db.models import IntegerField
from django.utils.translation import ugettext_lazy as _

from referral_project.utils.django.enums import IntEnumChoices


class CampaignKind(IntEnumChoices):
    VIDEO = 0
    WEBSITE = 1
    SURVEY = 2

    class Labels:
        VIDEO = _('Video')
        WEBSITE = _('Website')
        SURVEY = _('Survey')


CampaignKindField = partial(
    IntegerField,
    choices=CampaignKind.choices(),
    default=CampaignKind.VIDEO,
)
