from factory import DjangoModelFactory, Iterator, SubFactory, LazyAttribute

from referral_project.transactions.fields import Action
from referral_project.transactions.models import Transaction
from referral_project.utils.django.fields import ProcessStatus
from referral_project.wallets.tests.factories import WalletFactory, TransferReceiverWalletFactory, \
    TransferSenderWalletFactory, DepositSenderWalletFactory, DepositReceiverWalletFactory, \
    WithdrawalSenderWalletFactory, WithdrawalReceiverWalletFactory


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = Transaction

    action = Iterator(Action, getter=lambda c: c)
    sender = SubFactory(WalletFactory)
    receiver = SubFactory(WalletFactory)
    status = Iterator(ProcessStatus, getter=lambda c: c)


class DepositTransactionFactory(TransactionFactory):
    action = LazyAttribute(lambda o: Action.DEPOSIT)
    sender = SubFactory(DepositSenderWalletFactory)
    receiver = SubFactory(DepositReceiverWalletFactory)


class WithdrawalTransactionFactory(TransactionFactory):
    action = LazyAttribute(lambda o: Action.WITHDRAW)
    sender = SubFactory(WithdrawalSenderWalletFactory)
    receiver = SubFactory(WithdrawalReceiverWalletFactory)


class TransferTransactionFactory(TransactionFactory):
    action = LazyAttribute(lambda o: Action.TRANSFER)
    sender = SubFactory(TransferSenderWalletFactory)
    receiver = SubFactory(TransferReceiverWalletFactory)
