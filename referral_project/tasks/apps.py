from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TasksConfig(AppConfig):
    name = 'referral_project.tasks'
    verbose_name = _("Tasks")

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # noqa
