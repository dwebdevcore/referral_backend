from itertools import permutations

import pytest
from django.core.exceptions import ValidationError

from referral_project.campaigns.fields import CampaignKind
from referral_project.campaigns.tests.factories import CampaignFactory
from referral_project.tasks.tests.factories import TaskFactory
from referral_project.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'campaign_kind,task_kind',
    [(c, [t1, t2]) for c, t1, t2 in permutations([e.value for e in CampaignKind], 3)]
)
def test_raises_when_task_kind_mismatched_campaign_kind(
    campaign_kind: int,
    task_kind: int
):
    campaign = CampaignFactory(kind=campaign_kind)

    with pytest.raises(ValidationError):
        TaskFactory(
            kind=task_kind,
            campaign=campaign,
        )


@pytest.mark.parametrize('max_interactions', range(1, 3))
def test_task_expired_when_max_interactions_reached(max_interactions: int):
    task = TaskFactory(max_interactions=max_interactions)

    for i in range(max_interactions):
        task.interact(UserFactory())

    task.refresh_from_db()
    assert task.expired


@pytest.mark.parametrize('max_interactions', range(1, 3))
def test_raises_when_interacting_with_expired_task(max_interactions: int):
    task = TaskFactory(max_interactions=max_interactions)

    for i in range(max_interactions):
        task.interact(UserFactory())

    with pytest.raises(ValidationError):
        task.interact(UserFactory())
