from datetime import timedelta, date

import pytest
from django.utils.timezone import now

from referral_project.campaigns.tests.factories import CampaignFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('duration', [
    timedelta(minutes=4),
    timedelta(hours=3),
    timedelta(days=2),
    timedelta(weeks=1),
])
@pytest.mark.parametrize('finished_at', [
    now() - timedelta(minutes=8),
    now() - timedelta(hours=7),
    now() - timedelta(days=6),
    now() - timedelta(weeks=5),
])
def test_campaign_expired(
    duration: timedelta,
    finished_at: date,
):
    campaign = CampaignFactory(
        started_at=finished_at - duration,
        finished_at=finished_at
    )

    assert campaign.expired()

# TODO: this is yet to be implemented:
# TODO: https://trello.com/c/VVHAsRnz/30-check-campaignexpired-before-displaying-any-new-campaign-tasks-to-any-user
# TODO: so no testing for total rewards beyond budget for now
