from rest_framework import viewsets, mixins
from referral_project.payment_method.api.v0.serializers import PaymentMethodSerializer
from referral_project.payment_method.models import PaymentMethod
from referral_project.payment_method.fields import PaymentMethodOption


class PaymentMethods(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PaymentMethodSerializer

    def get_queryset(self):
        filter = self.request.GET.get('filter', None)
        if filter == 'deposit':
            return PaymentMethod.objects.filter(option=PaymentMethodOption.DEPOSIT)
        if filter == 'withdraw':
            return PaymentMethod.objects.filter(option=PaymentMethodOption.WITHDRAW)
        else:
            return PaymentMethod.objects.all()
