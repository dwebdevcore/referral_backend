from django.contrib import admin
from referral_project.transactions.models import Transaction, Deposit, Withdraw
from referral_project.utils.django.admin import TimeStampedModelAdmin
from referral_project.utils.django.fields import ProcessStatus
from referral_project.transactions.fields import Action
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from referral_project.payment_method.models import PaymentInformation
from referral_project.payment_method.fields import PaymentMethodOption


def process_transaction(modeladmin, request, queryset):
    for field in queryset.all():
        field.status=ProcessStatus.COMPLETED
        field.save()

def decline_transaction(modeladmin, request, queryset):
    for field in queryset.all():
        field.status=ProcessStatus.CANCELLED
        field.save()

@admin.register(Transaction)
class TransactionAdmin(TimeStampedModelAdmin):
    def get_queryset(self, request):
        qs = super(TransactionAdmin, self).get_queryset(request)
        return qs.exclude(action__in=[Action.WITHDRAW, Action.DEPOSIT])

    list_display = [
        'action',
        'amount',
        'sender',
        'receiver',
        'status',
    ]
    list_select_related = [
        'sender__user',
        'receiver__user',
    ]

@admin.register(Withdraw)
class WithdrawAdmin(TimeStampedModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(WithdrawAdmin, self).get_form(request, obj=obj, **kwargs)
        form.base_fields['action'].initial = int(Action.WITHDRAW)
        form.base_fields['payment_method'].queryset = PaymentInformation.objects.filter(
            payment_method__option=PaymentMethodOption.WITHDRAW)
        return form

    def get_queryset(self, request):
        qs = super(WithdrawAdmin, self).get_queryset(request)
        return qs.filter(action=Action.WITHDRAW)

    def available(self, obj):
        return obj.sender.balance

    list_display = [
        'action',
        'amount',
        'available',
        'status',
        'payment_method',
    ]

    list_select_related = [
        'sender__user',
        'receiver__user',
    ]
    actions = [
        process_transaction,
        decline_transaction,
    ]

@admin.register(Deposit)
class DepositAdmin(TimeStampedModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(DepositAdmin, self).get_form(request, obj=obj, **kwargs)
        form.base_fields['action'].initial = int(Action.DEPOSIT)
        form.base_fields['payment_method'].queryset = PaymentInformation.objects.filter(
            payment_method__option=PaymentMethodOption.DEPOSIT)
        return form

    def get_queryset(self, request):
        qs = super(DepositAdmin, self).get_queryset(request)
        return qs.filter(action=Action.DEPOSIT)

    def available(self, obj):
        return obj.receiver.balance

    list_display = [
        'action',
        'amount',
        'available',
        'status',
        'transaction_id',
    ]
    list_filter = [
        ('created', DateRangeFilter),
        ('modified', DateRangeFilter),
    ]
    actions = [
        process_transaction,
        decline_transaction,
    ]
