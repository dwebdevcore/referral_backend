from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import CASCADE, ForeignKey, CharField
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from referral_project.transactions.fields import ActionField, Action
from referral_project.users.fields import ActivatedDeactivatedStatus
from referral_project.utils.django.errors import INVALID_ERROR_CODE, BUSINESS_LOGIC_ERROR_CODE
from referral_project.utils.django.fields import ProcessStatusField, ProcessStatus
from referral_project.utils.djmoney.models.fields import ProjectMoneyField, ProjectMoney
from referral_project.wallets.fields import WalletKind
from referral_project.wallets.models import Wallet
from referral_project.payment_method.models import PaymentInformation


class Transaction(TimeStampedModel):
    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    # fields = ('action', 'amount', 'sender', 'receiver')
    action = ActionField()
    amount = ProjectMoneyField()
    sender = ForeignKey(
        Wallet,
        related_name='outgoing_transactions',
        on_delete=CASCADE,
    )
    receiver = ForeignKey(
        Wallet,
        related_name='incoming_transactions',
        on_delete=CASCADE,
    )
    status = ProcessStatusField()
    transaction_id = CharField(max_length=255, null=True, blank=True, verbose_name='Transaction ID')
    payment_method = ForeignKey(
        PaymentInformation,
        on_delete=CASCADE,
        null=True,
        blank=True,
        verbose_name='Payment Information',
    )

    def __str__(self):
        return f"{ProcessStatus(self.status).label} " \
               f"{self.amount} " \
               f"from #{self.sender_id} " \
               f"to #{self.receiver_id} " \
               f"(#{self.pk})"

    def clean(self):
        self._validate_business_logic()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def _validate_business_logic(self):
        self._validate_amount_greater_than_zero()
        self._validate_sender_balance_never_below_minimum()
        self._validate_sender_and_receiver_users_differ()
        self._validate_transferring_to_transfer_wallet()
        self._validate_transferring_at_least_minimum()
        self._validate_crediting_rewards_to_main_wallet()
        self._validate_crediting_referral_bonuses_to_referral_wallet()
        self._validate_withdrawing_at_least_minimum()
        self._validate_withdrawal_from_main_or_referral_wallet()
        self._validate_withdrawal_to_external_wallet()
        self._validate_sender_has_at_least_one_referral_prior_to_withdrawal()
        self._validate_withdrawing_user_activated()
        self._validate_depositing_from_external_wallet()
        self._validate_depositing_to_main_or_referral_or_transfer_wallet()

    def _validate_amount_greater_than_zero(self):
        if self.amount == ProjectMoney(amount=0):
            raise ValidationError(
                _("Zero-amount transaction does not make sense."),
                code=INVALID_ERROR_CODE,
            )

    def _validate_sender_balance_never_below_minimum(self):
        # Disable checking for DEPOSIT action from External wallet.
        # Let's assume that the External wallet is always
        # greater than the minimum sender's balance.

        if self.action == Action.WITHDRAW and self.sender.kind == WalletKind.REFERRAL:
            minimum_sender_balance = ProjectMoney(amount=settings.MINIMUM_REFER_SENDER_BALANCE)
        else:
            minimum_sender_balance = ProjectMoney(amount=settings.MINIMUM_SENDER_BALANCE)
        sender_balance_remainder = self.sender.balance - self.amount
        if sender_balance_remainder < minimum_sender_balance:
            raise ValidationError(
                _("No transaction leaving sender's wallet balance below %(msb)s is allowed."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={'msb': minimum_sender_balance},
            )

    def _validate_transferring_to_transfer_wallet(self):
        if self.action == Action.TRANSFER and self.receiver.kind != WalletKind.TRANSFER:
            raise ValidationError(
                _("Transfers are allowed to %(transfer)s wallets only."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={'transfer': WalletKind.TRANSFER.label},
            )

    def _validate_transferring_at_least_minimum(self):
        minimum_transfer_amount = ProjectMoney(amount=settings.MINIMUM_TRANSFER_AMOUNT)
        if self.action == Action.TRANSFER \
            and self.amount < minimum_transfer_amount:
            raise ValidationError(
                _("Transferring less than %(mta)s is not allowed."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={'mta': minimum_transfer_amount},
            )

    def _validate_crediting_rewards_to_main_wallet(self):
        if self.action == Action.REWARD and self.receiver.kind != WalletKind.MAIN:
            raise ValidationError(
                _("Crediting rewards is allowed to %(main)s wallets only."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={'main': WalletKind.MAIN.label},
            )

    def _validate_crediting_referral_bonuses_to_referral_wallet(self):
        if self.action == Action.REFERRAL_BONUS and self.receiver.kind != WalletKind.REFERRAL:
            raise ValidationError(
                _("Crediting referrals is allowed to %(referral)s wallets only."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={'referral': WalletKind.REFERRAL.label},
            )

    def _validate_withdrawal_from_main_or_referral_wallet(self):
        if self.action == Action.WITHDRAW \
            and self.sender.kind not in {WalletKind.MAIN, WalletKind.REFERRAL}:
            raise ValidationError(
                _("Withdrawals are only allowed from %(main)s and %(referral)s wallets."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={
                    'main': WalletKind.MAIN.label,
                    'referral': WalletKind.REFERRAL.label,
                },
            )

    def _validate_withdrawal_to_external_wallet(self):
        if self.action == Action.WITHDRAW \
            and self.receiver.kind != WalletKind.EXTERNAL:
            raise ValidationError(
                _("Withdrawals are only allowed to %(external)s wallets."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={'external': WalletKind.EXTERNAL.label},
            )

    def _validate_sender_has_at_least_one_referral_prior_to_withdrawal(self):
        if self.action == Action.WITHDRAW \
            and self.sender.user.referrals.count() == 0:
            raise ValidationError(
                _("Withdrawals are only allowed after at least one referral signed up."),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )

    def _validate_withdrawing_at_least_minimum(self):
        if self.action == Action.WITHDRAW \
            and self.amount < ProjectMoney(amount=settings.MINIMUM_WITHDRAWAL_AMOUNT)\
            and self.sender.kind != WalletKind.REFERRAL:
            raise ValidationError(
                _("Withdrawing less than %(mwa)s is not allowed."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={'mwa': ProjectMoney(amount=settings.MINIMUM_WITHDRAWAL_AMOUNT)},
            )

    def _validate_depositing_from_external_wallet(self):
        if self.action == Action.DEPOSIT \
            and self.sender.kind != WalletKind.EXTERNAL:
            raise ValidationError(
                _("Deposits are only allowed from %(external)s wallets."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={'external': WalletKind.EXTERNAL.label},
            )

    def _validate_withdrawing_user_activated(self):
        if self.action == Action.WITHDRAW \
            and self.sender.user.status == ActivatedDeactivatedStatus.DEACTIVATED:
            raise ValidationError(
                _("Withdrawals are only allowed for activated users."),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )

    def _validate_depositing_to_main_or_referral_or_transfer_wallet(self):
        if self.action == Action.DEPOSIT \
            and self.receiver.kind not in {WalletKind.MAIN, WalletKind.REFERRAL, WalletKind.TRANSFER}:
            raise ValidationError(
                _("Deposits are only allowed to %(main)s, %(referral)s, %(transfer)s wallets."),
                code=BUSINESS_LOGIC_ERROR_CODE,
                params={
                    'main': WalletKind.MAIN.label,
                    'referral': WalletKind.REFERRAL.label,
                    'transfer': WalletKind.TRANSFER.label,
                },
            )

    def _validate_sender_and_receiver_users_differ(self):
        if self.receiver.user == self.sender.user and self.action != Action.DEPOSIT and self.action != Action.WITHDRAW:
            raise ValidationError(
                _("One cannot initiate transactions between their own wallets."),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )

class Deposit(Transaction):
    class Meta:
        proxy = True


class Withdraw(Transaction):
    class Meta:
        proxy = True
