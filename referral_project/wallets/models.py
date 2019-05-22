from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, AbstractUser, User
from django.db.models import CASCADE, ForeignKey
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from referral_project.utils.djmoney.models.fields import ProjectMoney, ProjectMoneyField
from referral_project.wallets.fields import WalletKindField, WalletKind


class Wallet(TimeStampedModel):
    class Meta:
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")
        unique_together = [
            'user',
            'kind'
        ]

    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='wallets',
        on_delete=CASCADE,
    )
    kind = WalletKindField()
    balance = ProjectMoneyField()

    def __str__(self):
        return f"{self.user.username}'s " \
               f"{WalletKind(self.kind).label} " \
               f"({self.balance})"


def get_balance(user, kind):
    return str(Wallet.objects.filter(user=user, kind=kind).first().balance)
