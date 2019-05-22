from rest_framework.serializers import ModelSerializer

from referral_project.tasks.models import Task


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'name',
            'kind',
            'link',
            'reward',
            'campaign',
            'status',
            'max_interactions',
            'expired',
        ]
