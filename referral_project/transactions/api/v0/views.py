from rest_framework import viewsets, mixins
from rest_framework import decorators
from referral_project.transactions.api.v0.serializers import TransactionSerializer, TransferSerializer, DepositSerializer, WithdrawSerializer
from referral_project.transactions.models import Transaction
from referral_project.wallets.models import get_balance
from referral_project.wallets.fields import WalletKind
from django.db.models import Q
from datetime import datetime
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.utils.translation import ugettext_lazy as _


class Transactions(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def get_queryset(self):
        query_set = super(Transactions, self).get_queryset()
        if self.action == 'show':
            start_date = self.request.GET.get('start_date', '2016-01-01')
            end_date = self.request.GET.get('end_date', datetime.now())
            query_set = query_set.filter(Q(sender__user=self.request.user) | Q(receiver__user=self.request.user),
                                         modified__range=[start_date, end_date])
        return query_set

    def get_serializer_class(self):
        if self.action == 'transfer':
            return TransferSerializer
        if self.action == 'deposit':
            return DepositSerializer
        if self.action == 'withdraw':
            return WithdrawSerializer
        return TransactionSerializer

    @decorators.list_route(methods=['post', ])
    def deposit(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={'detail': _("Deposit request has been created.")},
            status=HTTP_200_OK,
        )

    @decorators.list_route(methods=['post', ])
    def withdraw(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={'detail': _("Withdraw request has been created.")},
            status=HTTP_200_OK,
        )

    @decorators.list_route(methods=['get', ])
    def show(self, request, *args, **kwargs):
        resp = super(Transactions, self).list(request, *args, **kwargs)
        resp.data['transfer_balance'] = get_balance(self.request.user, WalletKind.TRANSFER)
        resp.data['main_balance'] = get_balance(self.request.user, WalletKind.MAIN)
        resp.data['referral_balance'] = get_balance(self.request.user, WalletKind.REFERRAL)
        return resp

    @decorators.list_route(methods=['post', ])
    def transfer(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={'detail': _("Transfer request has been created.")},
            status=HTTP_200_OK,
        )
