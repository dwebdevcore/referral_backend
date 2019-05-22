from rest_framework.serializers import ModelSerializer

from referral_project.wallets.models import Wallet


class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            'id',
            'user',
            'kind',
            'balance',
        ]
        extra_kwargs = {
            'balance': {
                'read_only': True,
            }
        }
