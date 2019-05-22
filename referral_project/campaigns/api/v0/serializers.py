from rest_framework.serializers import ModelSerializer

from referral_project.campaigns.models import Campaign


class CampaignSerializer(ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            'id',
            'name',
            'kind',
            'started_at',
            'finished_at',
            'prototype',
            'budget',
            'status',
        ]
