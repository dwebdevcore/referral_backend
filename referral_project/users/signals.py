from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from referral_project.wallets.fields import WalletKind
from referral_project.wallets.models import Wallet


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallets(sender, instance=None, created=False, **kwargs):
    if created:
        Wallet.objects.bulk_create([
            Wallet(user=instance, kind=WalletKind.MAIN),
            Wallet(user=instance, kind=WalletKind.TRANSFER),
            Wallet(user=instance, kind=WalletKind.REFERRAL),
            Wallet(user=instance, kind=WalletKind.EXTERNAL),
        ])
