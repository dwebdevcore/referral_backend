from rest_framework import viewsets, mixins
from referral_project.wallets.api.v0.serializers import WalletSerializer
from referral_project.wallets.models import Wallet


class Wallets(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = WalletSerializer

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
