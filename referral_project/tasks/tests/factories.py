from factory import DjangoModelFactory, SubFactory, Faker, Iterator, LazyAttribute

from referral_project.campaigns.tests.factories import CampaignFactory
from referral_project.tasks.models import Task, TaskStatus
from referral_project.users.tests.factories import UserFactory
from referral_project.utils.django.fields import ActiveInactiveStatus


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    name = Faker('company')
    campaign = SubFactory(CampaignFactory)
    kind = LazyAttribute(lambda o: o.campaign.kind)
    link = Faker('url')
    # TODO: reward
    status = Iterator(ActiveInactiveStatus, getter=lambda c: c)
    max_interactions = Faker('pyint')


class TaskStatusFactory(DjangoModelFactory):
    class Meta:
        model = TaskStatus

    interacted = Faker('pybool')
    user = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)
