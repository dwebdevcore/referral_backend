from django.contrib import admin

from referral_project.utils.django.admin import TimeStampedModelAdmin
from referral_project.payment_method.models import PaymentMethod, PaymentInformation


@admin.register(PaymentMethod)
class PaymentMethodAdmin(TimeStampedModelAdmin):
    list_display = [
        'name',
        'option',
    ]
    list_filter = [
        'option',
    ]

@admin.register(PaymentInformation)
class PaymentInformationAdmin(TimeStampedModelAdmin):
    list_display = [
        'email',
        'payment_method',
    ]
    list_filter = [
        'payment_method__option',
    ]
