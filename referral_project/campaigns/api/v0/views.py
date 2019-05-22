from rest_framework.decorators import detail_route
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework import viewsets, mixins
from referral_project.campaigns.api.v0.serializers import CampaignSerializer
from referral_project.campaigns.models import Campaign


class Campaigns(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CampaignSerializer
    queryset = Campaign.objects.all()

    @detail_route(methods=['post'])
    def start(self, request: Request, pk: int = None) -> Response:
        campaign = self.get_object()

        campaign.start()

        return Response(status=HTTP_200_OK)

    @detail_route(methods=['post'])
    def finish(self, request: Request, pk: int = None) -> Response:
        campaign = self.get_object()

        campaign.finish()

        return Response(status=HTTP_200_OK)
