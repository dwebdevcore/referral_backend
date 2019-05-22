from django.contrib import admin

from referral_project.utils.django.admin import TimeStampedModelAdmin
from referral_project.wallets.models import Wallet


@admin.register(Wallet)
class WalletAdmin(TimeStampedModelAdmin):
    list_display = [
        'user',
        'kind',
        'balance',
    ]
