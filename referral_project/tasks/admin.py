from django.contrib import admin

from referral_project.tasks.models import Task, TaskStatus
from referral_project.utils.django.admin import TimeStampedModelAdmin


@admin.register(Task)
class TaskAdmin(TimeStampedModelAdmin):
    list_display = [
        'name',
        'kind',
        'link',
        'reward',
        'campaign',
        'status',
        'max_interactions',
        'expired',
    ]

    list_filter = [
        'kind'
    ]


@admin.register(TaskStatus)
class TaskStatusAdmin(TimeStampedModelAdmin):
    list_display = [
        'interacted',
    ]
