from rest_framework.serializers import ModelSerializer

from referral_project.transactions.models import Transaction
from referral_project.wallets.models import Wallet
from referral_project.wallets.fields import WalletKind
from referral_project.payment_method.models import PaymentInformation, PaymentMethod
from referral_project.utils.django.fields import ProcessStatus
from referral_project.transactions.fields import Action
from django.core.exceptions import ValidationError
from referral_project.utils.django.errors import BUSINESS_LOGIC_ERROR_CODE
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'action',
            'amount',
            'sender',
            'receiver',
            'status',
            'modified',
            'created',
        ]

    def validate_sender(self, value: str):
        if value.user != self.context.get('request').user:
            raise ValidationError(
                _("Sender should be current user."),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )
        return value


class TransferSerializer(ModelSerializer):
    username = serializers.CharField(required=True)

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'sender',
            'username',
        ]

    def validate_sender(self, value: str):
        if value.user != self.context.get('request').user:
            raise ValidationError(
                _("Sender should be current user."),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )
        return value

    def validate_username(self, value: str):
        receiver = Wallet.objects.filter(user__username=value, kind=WalletKind.TRANSFER)
        if not receiver.exists():
            raise ValidationError(
                _("Username is not correct, please input valid username"),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )
        return receiver.first()

    def create(self, validated_data):
        transaction = Transaction.objects.create(action=Action.TRANSFER,
                                   sender=validated_data.get('sender'),
                                   receiver=validated_data.get('username'),
                                   amount=validated_data.get('amount'),
                                   status=ProcessStatus.COMPLETED)
        return transaction


class DepositSerializer(ModelSerializer):
    payment_method = serializers.IntegerField()
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'payment_method',
            'transaction_id',
        ]

    def create(self, validated_data):
        sender = Wallet.objects.filter(user__is_superuser=True, kind=WalletKind.EXTERNAL).first()
        receiver = Wallet.objects.filter(user=self.context.get('request').user, kind=WalletKind.MAIN).first()
        payment_info = PaymentInformation.objects.filter(
            payment_method_id=validated_data.get('payment_method')
        )
        if payment_info.exists():
            payment_info = payment_info.first()
        else:
            payment_info = None
        transaction = Transaction.objects.create(
            action=Action.DEPOSIT,
            sender=sender,
            receiver=receiver,
            amount=validated_data.get('amount'),
            payment_method=payment_info,
            transaction_id=validated_data.get('transaction_id')
        )
        return transaction


class WithdrawSerializer(ModelSerializer):
    payment_method = serializers.IntegerField()
    email = serializers.CharField(required=True)
    class Meta:
        model = Transaction
        fields = [
            'sender',
            'payment_method',
            'amount',
            'email',
        ]

    def validate_sender(self, value: str):
        if value.user != self.context.get('request').user:
            raise ValidationError(
                _("Sender should be current user."),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )

        if Transaction.objects.filter(sender=value, status=ProcessStatus.PENDING, action=Action.WITHDRAW).exists():
            raise ValidationError(
                _("You can't process withdraw request since you have pending withdraw request, ."),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )
        return value

    def create(self, validated_data):
        receiver = Wallet.objects.filter(user=self.context.get('request').user, kind=WalletKind.EXTERNAL).first()
        #todo use update_or_create
        payment_method = PaymentMethod.objects.filter(pk=validated_data.get('payment_method')).first()
        payment_info = PaymentInformation.objects.create(
            email=validated_data.get('email'),
            payment_method=payment_method
        )

        transaction = Transaction.objects.create(
            action=Action.WITHDRAW,
            sender=validated_data.get('sender'),
            receiver=receiver,
            amount=validated_data.get('amount'),
            payment_method=payment_info,
        )
        return transaction
