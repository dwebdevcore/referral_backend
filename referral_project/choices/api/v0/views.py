import operator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ViewSet

from referral_project.campaigns.fields import CampaignKind
from referral_project.transactions.fields import Action
from referral_project.users.fields import ActivatedDeactivatedStatus
from referral_project.utils.django.fields import ActiveInactiveStatus, ProcessStatus
from referral_project.wallets.fields import WalletKind


class Choices(ViewSet):
    http_method_names = ['get', ]
    choices_map = {
        'campaign-kind': CampaignKind.choices(),
        'active-inactive-status': ActiveInactiveStatus.choices(),
        'action': Action.choices(),
        'process-status': ProcessStatus.choices(),
        'activated-deactivated-status': ActivatedDeactivatedStatus.choices(),
        'wallet-kind': WalletKind.choices(),
    }

    @staticmethod
    def format_item(item):
        k, v = item
        return {'value': k, 'title': str(v)}

    def prepare(self, choices):
        return list(map(self.format_item, choices))

    @staticmethod
    def search_by_title(choices, search):
        if search is not None:
            choices = filter(
                lambda x: search.lower() in x.get('title').lower(),
                choices
            )
        return list(choices)

    @staticmethod
    def order_by_title(choices):
        if choices:
            choices.sort(key=operator.itemgetter('title'))
        return choices

    def retrieve(self, request, pk=None):
        """
        Return data for choices fields by {id}.
        - id - choices field name.
        """
        search = request.GET.get('search')

        if pk not in self.choices_map:
            return Response(status=status.HTTP_404_NOT_FOUND)

        choices = self.choices_map.get(pk)
        choices = self.prepare(choices)
        choices = self.search_by_title(choices, search)
        choices = self.order_by_title(choices)
        return Response(choices, status=status.HTTP_200_OK)

    def list(self, request):
        """
        Return names of choices fields.
        """
        data = {}
        for k, v in self.choices_map.items():
            url = reverse('choices-detail', args=[k], request=request)
            data[k] = url
        return Response(data, status=status.HTTP_200_OK)
