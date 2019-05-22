from typing import Sequence, Any, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from factory import DjangoModelFactory, Faker, post_generation
from rest_framework.authtoken.models import Token

from referral_project.utils.rest_framework.test import StrictAPIClient


class TokenFactory(DjangoModelFactory):
    class Meta:
        model = Token
        django_get_or_create = [
            'user',
        ]


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = [
            'name',
        ]


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = [
            'email',
            'username',
        ]

    email = Faker('email')
    username = Faker('user_name')

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = Faker(
            'password',
            length=42,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True
        ).generate(extra_kwargs={})
        self.set_password(password)

    @post_generation
    def referrals(self, create: bool, extracted: Optional[Sequence[settings.AUTH_USER_MODEL]], **kwargs):
        self.referrals = extracted or []

    @post_generation
    def api_client(self, create, extracted, **kwargs):
        api_client = StrictAPIClient()
        api_client.force_authenticate(user=self)
        self.api_client = api_client
