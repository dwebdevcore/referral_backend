from rest_framework.serializers import ModelSerializer

from referral_project.payment_method.models import PaymentMethod, PaymentInformation


class PaymentInformationSerializer(ModelSerializer):
    class Meta:
        model = PaymentInformation
        fields = [
            'email',
        ]


class PaymentMethodSerializer(ModelSerializer):
    payment_information = PaymentInformationSerializer(many=True, read_only=True)
    class Meta:
        model = PaymentMethod
        fields = [
            'name',
            'id',
            'payment_information',
        ]
