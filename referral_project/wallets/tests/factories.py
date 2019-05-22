from typing import Optional

from django.conf import settings
from factory import DjangoModelFactory, SubFactory, Iterator, post_generation, LazyAttribute
from faker import Faker

from referral_project.users.tests.factories import UserFactory
from referral_project.utils.djmoney.models.fields import ProjectMoney
from referral_project.wallets.fields import WalletKind
from referral_project.wallets.models import Wallet


class WalletFactory(DjangoModelFactory):
    class Meta:
        model = Wallet
        django_get_or_create = [
            'user',
            'kind',
        ]

    user = SubFactory(UserFactory)
    kind = Iterator(WalletKind, getter=lambda c: c)

    @post_generation
    def balance(self, create: bool, extracted: Optional[ProjectMoney], **kwargs):
        if extracted is not None:
            self.balance = extracted
        else:
            self.balance = ProjectMoney(amount=settings.MINIMUM_SENDER_BALANCE + Faker().pyint())


class DepositSenderWalletFactory(WalletFactory):
    kind = LazyAttribute(lambda o: WalletKind.EXTERNAL)

    @post_generation
    def balance(self, create: bool, extracted: Optional[ProjectMoney], **kwargs):
        if extracted is not None:
            self.balance = extracted
        else:
            self.balance = ProjectMoney(amount=settings.MINIMUM_TRANSFER_BALANCE + Faker().pyint())


class DepositReceiverWalletFactory(WalletFactory):
    kind = Iterator([
        k for k in WalletKind
        if k != WalletKind.EXTERNAL
    ], getter=lambda c: c)


class WithdrawalSenderWalletFactory(WalletFactory):
    kind = Iterator([
        k for k in WalletKind
        if k in {WalletKind.MAIN, WalletKind.REFERRAL}
    ], getter=lambda c: c)

    # TODO: user__referrals=[UserFactory()]

    @post_generation
    def balance(self, create: bool, extracted: Optional[ProjectMoney], **kwargs):
        if extracted is not None:
            self.balance = extracted
        else:
            self.balance = ProjectMoney(amount=settings.MINIMUM_WITHDRAWAL_BALANCE + Faker().pyint())


class WithdrawalReceiverWalletFactory(WalletFactory):
    kind = LazyAttribute(lambda o: WalletKind.EXTERNAL)


class TransferSenderWalletFactory(WalletFactory):
    kind = Iterator([k for k in WalletKind], getter=lambda c: c)

    # TODO: user__referrals=[UserFactory()]

    @post_generation
    def balance(self, create: bool, extracted: Optional[ProjectMoney], **kwargs):
        if extracted is not None:
            self.balance = extracted
        else:
            self.balance = ProjectMoney(amount=settings.MINIMUM_TRANSFER_BALANCE + Faker().pyint())


class TransferReceiverWalletFactory(WalletFactory):
    kind = LazyAttribute(lambda o: WalletKind.TRANSFER)
