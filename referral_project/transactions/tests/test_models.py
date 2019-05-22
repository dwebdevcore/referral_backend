import pytest
from django.conf import settings
from django.core.exceptions import ValidationError

from referral_project.transactions.fields import Action
from referral_project.transactions.tests.factories import TransactionFactory, TransferTransactionFactory, \
    WithdrawalTransactionFactory
from referral_project.users.fields import ActivatedDeactivatedStatus
from referral_project.users.tests.factories import UserFactory
from referral_project.utils.djmoney.models.fields import ProjectMoney
from referral_project.wallets.fields import WalletKind
from referral_project.wallets.tests.factories import WalletFactory, WithdrawalSenderWalletFactory, \
    WithdrawalReceiverWalletFactory, TransferSenderWalletFactory, TransferReceiverWalletFactory

pytestmark = pytest.mark.django_db


def test_wallets_balanced_after_transaction():
    amount = ProjectMoney(amount=settings.MINIMUM_TRANSFER_AMOUNT)
    sender = TransferSenderWalletFactory()
    sender_balance = sender.balance
    receiver = TransferReceiverWalletFactory()
    receiver_balance = receiver.balance

    TransferTransactionFactory(
        amount=amount,
        sender=sender,
        receiver=receiver,
    )

    sender.refresh_from_db()
    assert sender.balance == sender_balance - amount
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance + amount


def test_raises_when_zero_amount_transaction():
    zero = ProjectMoney(amount=0)
    sender = WalletFactory(balance=zero)
    receiver = WalletFactory()
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=zero,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == zero
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


def test_raises_when_sender_does_not_have_enough_balance():
    sender = WalletFactory()
    sender_balance = sender.balance
    receiver = WalletFactory()
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance * 2,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


def test_raises_when_sender_balance_less_than_minimum():
    sender_balance = ProjectMoney(amount=settings.MINIMUM_SENDER_BALANCE - 1)
    sender = WalletFactory(balance=sender_balance)
    receiver = WalletFactory()
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


@pytest.mark.parametrize(
    'non_transfer_receiver_kind',
    [k for k in WalletKind if k != WalletKind.TRANSFER],
)
def test_raises_when_transferring_to_any_wallet_other_than_transfer(
    non_transfer_receiver_kind: WalletKind,
):
    sender = WalletFactory()
    sender_balance = sender.balance
    receiver = WalletFactory(kind=non_transfer_receiver_kind)
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            action=Action.TRANSFER,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


def test_raises_when_not_enough_balance_to_transfer():
    # TODO: (lazy) settings
    sender_balance = ProjectMoney(amount=settings.MINIMUM_TRANSFER_BALANCE)
    sender = TransferSenderWalletFactory(balance=sender_balance, user__referrals=[UserFactory()])
    receiver = TransferReceiverWalletFactory()
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=ProjectMoney(amount=settings.MINIMUM_TRANSFER_AMOUNT - 1),
            action=Action.TRANSFER,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


@pytest.mark.parametrize(
    'non_main_receiver_kind',
    [k for k in WalletKind if k != WalletKind.MAIN]
)
def test_raises_when_crediting_reward_to_any_wallet_other_than_main(
    non_main_receiver_kind: WalletKind,
):
    sender = WalletFactory()
    sender_balance = sender.balance
    receiver = WalletFactory(kind=non_main_receiver_kind)
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            action=Action.REWARD,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


@pytest.mark.parametrize(
    'invalid_receiver_kind',
    [k for k in WalletKind if k != WalletKind.REFERRAL]
)
def test_raises_when_crediting_referral_bonus_to_any_wallet_other_than_referral(
    invalid_receiver_kind: WalletKind,
):
    sender = WalletFactory()
    sender_balance = sender.balance
    receiver = WalletFactory(kind=invalid_receiver_kind)
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            action=Action.REFERRAL_BONUS,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


@pytest.mark.parametrize(
    'invalid_sender_kind',
    [k for k in WalletKind if k not in {WalletKind.MAIN, WalletKind.REFERRAL}]
)
def test_raises_when_withdrawing_from_any_wallet_other_than_main_or_referral(
    invalid_sender_kind: WalletKind,
):
    sender = WalletFactory(kind=invalid_sender_kind)
    sender_balance = sender.balance
    receiver = WalletFactory()
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            action=Action.WITHDRAW,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


@pytest.mark.parametrize(
    'invalid_receiver_kind',
    [k for k in WalletKind if k != WalletKind.EXTERNAL]
)
def test_raises_when_withdrawing_to_any_wallet_other_than_external(
    invalid_receiver_kind: WalletKind,
):
    sender = WalletFactory()
    sender_balance = sender.balance
    receiver = WalletFactory(kind=invalid_receiver_kind)
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            action=Action.WITHDRAW,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


def test_raises_when_none_referrals_prior_to_withdrawal():
    sender = WithdrawalSenderWalletFactory()
    sender_balance = sender.balance
    receiver = WithdrawalReceiverWalletFactory()
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            action=Action.WITHDRAW,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


def test_raises_when_not_enough_balance_to_withdraw():
    # TODO: (lazy) settings
    sender_balance = ProjectMoney(amount=settings.MINIMUM_WITHDRAWAL_BALANCE)
    sender = WithdrawalSenderWalletFactory(balance=sender_balance, user__referrals=[UserFactory()])
    receiver = WithdrawalReceiverWalletFactory()
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=ProjectMoney(amount=settings.MINIMUM_WITHDRAWAL_AMOUNT - 1),
            action=Action.WITHDRAW,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


@pytest.mark.parametrize('sender_kind', [WalletKind.EXTERNAL, ])
@pytest.mark.parametrize('invalid_reciever_kind', [WalletKind.EXTERNAL, ])
def test_raises_when_depositing_to_external_wallet(
    sender_kind: WalletKind,
    invalid_reciever_kind: WalletKind,
):
    sender = WalletFactory(kind=sender_kind)
    sender_balance = sender.balance
    receiver = WalletFactory(kind=invalid_reciever_kind)
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            action=Action.DEPOSIT,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


@pytest.mark.parametrize(
    'invalid_sender_kind',
    [k for k in WalletKind if k != WalletKind.EXTERNAL]
)
@pytest.mark.parametrize(
    'reciever_kind',
    [k for k in WalletKind if k != WalletKind.EXTERNAL]
)
def test_raises_when_depositing_from_any_wallet_other_than_external(
    invalid_sender_kind: WalletKind,
    reciever_kind: WalletKind,
):
    sender = WalletFactory(kind=invalid_sender_kind)
    sender_balance = sender.balance
    receiver = WalletFactory(kind=reciever_kind)
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=sender_balance,
            action=Action.DEPOSIT,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


def test_raises_when_same_sender_and_receiver():
    # TODO: parametrize
    user = UserFactory()
    sender = WalletFactory(user=user, kind=WalletKind.MAIN)
    sender_balance = sender.balance
    receiver = WalletFactory(user=user, kind=WalletKind.TRANSFER)
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        TransactionFactory(
            amount=ProjectMoney(100),
            action=Action.TRANSFER,
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance


@pytest.mark.parametrize('non_activated_user_status', [
    s for s in ActivatedDeactivatedStatus
    if s != ActivatedDeactivatedStatus.ACTIVATED
])
def test_raises_when_non_activated_user_withdrawing(
    non_activated_user_status: ActivatedDeactivatedStatus
):
    user = UserFactory(status=non_activated_user_status)
    sender = WithdrawalSenderWalletFactory(user=user, user__referrals=[UserFactory()])
    sender_balance = sender.balance
    receiver = WithdrawalReceiverWalletFactory()
    receiver_balance = receiver.balance

    with pytest.raises(ValidationError):
        WithdrawalTransactionFactory(
            amount=ProjectMoney(amount=settings.MINIMUM_WITHDRAWAL_AMOUNT),
            sender=sender,
            receiver=receiver,
        )
    sender.refresh_from_db()
    assert sender.balance == sender_balance
    receiver.refresh_from_db()
    assert receiver.balance == receiver_balance
