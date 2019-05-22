from django.contrib.auth import get_user_model
from referral_project.users.models import KYC
from rest_framework import serializers
from django.core.exceptions import ValidationError
from referral_project.utils.django.errors import BUSINESS_LOGIC_ERROR_CODE
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class KYCRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = [
            'first_name',
            'last_name',
            'address',
            'city',
            'country',
            'phone',
            'identification',
            'id_kind',
        ]

    def validate_identification(self, value: str):
        if self.context.get('request').user.customer is not None:
            raise ValidationError(
                _("KYC is already existed."),
                code=BUSINESS_LOGIC_ERROR_CODE,
            )
        return value

    def create(self, validated_data):
        customer = KYC.objects.create(**validated_data)
        return customer
