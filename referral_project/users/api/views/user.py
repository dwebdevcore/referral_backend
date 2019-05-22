from django.contrib.auth import get_user_model
from rest_framework import decorators
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime
from datetime import timedelta
from referral_project.wallets.models import Wallet
from referral_project.transactions.models import Transaction
from referral_project.transactions.fields import Action
from referral_project.utils.django.fields import ProcessStatus
from referral_project.wallets.fields import WalletKind
from referral_project.utils.djmoney.models.fields import ProjectMoney
from referral_project.users.fields import ActivatedDeactivatedStatus
from django.conf import settings

from ..serializers import (
    UserChangePasswordSerializer,
    UserRegisterSerializer,
    UserSerializer,
    KYCRegisterSerializer,
)

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):

    def get_queryset(self):
        queryset = User.objects.all()
        if self.action == 'referrals':
            queryset = queryset.filter(referrer=self.request.user)
            start_date = self.request.GET.get('start_date', '2016-01-01')
            end_date = self.request.GET.get('end_date', datetime.now())
            queryset = queryset.filter(referrer=self.request.user, date_joined__range=[start_date, end_date])
        return queryset

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegisterSerializer
        if self.action == 'change_password':
            return UserChangePasswordSerializer
        if self.action == 'kyc_post':
            return KYCRegisterSerializer
        return UserSerializer

    @decorators.list_route(methods=['get', ])
    def referrals(self, request, *args, **kwargs):
        return super(UserViewSet, self).list(request, *args, **kwargs)

    @decorators.list_route(methods=['get', ])
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.list_route(methods=['post', ], permission_classes=[AllowAny, ])
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_serializer = UserSerializer(user, context=self.get_serializer_context())
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)

    @decorators.list_route(methods=['post', ], url_path='change-password')
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password changed'}, status=status.HTTP_200_OK)

    @decorators.list_route(methods=['post', ], url_path='activate')
    def activate(self, request, *args, **kwargs):
        user = request.user
        if request.user.status==ActivatedDeactivatedStatus.ACTIVATED:
            return Response({'message': "It's already activated"},
                            status=status.HTTP_200_OK)
        activation_cost = ProjectMoney(amount=settings.ACTIVATION_COST)
        referral_bonus = ProjectMoney(amount=settings.REFERRAL_BONUS)
        main = Wallet.objects.filter(user=user, kind=WalletKind.MAIN).first()
        transfer = Wallet.objects.filter(user=user, kind=WalletKind.TRANSFER).first()
        refer = Wallet.objects.filter(user=user, kind=WalletKind.REFERRAL).first()
        super_main = Wallet.objects.filter(user__is_superuser=True, kind=WalletKind.MAIN).first()

        if main.balance > activation_cost:
            main.balance -= activation_cost
            main.save()
        elif transfer.balance > activation_cost:
            transfer.balance -= activation_cost
            transfer.save()
        elif refer.balance > activation_cost:
            refer.balance -= activation_cost
            refer.save()
        else:
            return Response({'message': "You haven't sufficient balance in any of your wallet"},
                            status=status.HTTP_400_BAD_REQUEST)

        super_main.balance += activation_cost
        if user.referrer is not None:
            referr_wallet = Wallet.objects.filter(user=user.referrer, kind=WalletKind.REFERRAL).first()
            super_refer = Wallet.objects.filter(user__is_superuser=True, kind=WalletKind.REFERRAL).first()
            Transaction.objects.create(action=Action.REFERRAL_BONUS,
                                       sender=super_refer,
                                       receiver=referr_wallet,
                                       amount=referral_bonus,
                                       status=ProcessStatus.COMPLETED)
        super_main.save()
        user.status=ActivatedDeactivatedStatus.ACTIVATED
        user.activation_date = datetime.now()
        user.expiration_date = datetime.now() + timedelta(days=90)
        user.save()
        return Response({'message': 'Congratulations! Your account has been activated'},
                        status=status.HTTP_200_OK)

    @decorators.list_route(methods=['post', ], url_path='kyc_post')
    def kyc_post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        request.user.customer = instance
        request.user.save()
        return Response({'message': 'KYC data is created'}, status=status.HTTP_200_OK)
