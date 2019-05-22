from factory import DjangoModelFactory, Iterator, Faker

from referral_project.campaigns.fields import CampaignKind
from referral_project.campaigns.models import Campaign
from referral_project.utils.django.fields import ActiveInactiveStatus


class CampaignFactory(DjangoModelFactory):
    class Meta:
        model = Campaign

    name = Faker('company')
    kind = Iterator(CampaignKind, getter=lambda c: c)
    status = Iterator(ActiveInactiveStatus, getter=lambda c: c)
    # TODO: budget
