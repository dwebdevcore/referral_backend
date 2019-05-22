from django.contrib import admin

from referral_project.campaigns.models import Campaign
from referral_project.utils.django.admin import TimeStampedModelAdmin


@admin.register(Campaign)
class CampaignAdmin(TimeStampedModelAdmin):
    list_display = [
        'name',
        'kind',
        'started_at',
        'finished_at',
        'prototype',
        'budget',
        'status',
    ]
