from django.db.models.signals import post_save
from django.dispatch import receiver

from referral_project.tasks.models import TaskStatus


@receiver(post_save, sender=TaskStatus)
def expire_task_when_max_interactions_reached(instance: TaskStatus, created: bool, **kwargs):
    task = instance.task
    total_task_interactions = TaskStatus.objects.filter(
        interacted=True,
        task=task,
    ).count()
    if total_task_interactions == task.max_interactions:
        task.expired = True
        task.save(update_fields={'expired'})
