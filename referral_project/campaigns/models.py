from typing import Optional

from django.db.models import CharField, ForeignKey, CASCADE, DateTimeField, Sum
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel, TimeFramedModel

from referral_project.campaigns.fields import CampaignKindField
from referral_project.utils.django.fields import ActiveInactiveStatusField, ActiveInactiveStatus
from referral_project.utils.djmoney.models.fields import ProjectMoneyField, ProjectMoney


class Campaign(TimeStampedModel):
    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    name = CharField(max_length=255)
    kind = CampaignKindField()
    started_at = DateTimeField(
        null=True, blank=True,
        verbose_name=_("Started at")
    )
    finished_at = DateTimeField(
        null=True, blank=True,
        verbose_name=_("Finished at")
    ) # TODO: validate not earlier than self.started_at (? third-parties)
    prototype = ForeignKey(
        'self',
        null=True, blank=True,
        related_name='derivatives',
        on_delete=CASCADE,
    )
    budget = ProjectMoneyField()
    status = ActiveInactiveStatusField()

    def expired(self) -> bool:
        n = now()
        # TODO: acting retroactively -- a proactive approach must rather be taken (https://trello.com/c/VVHAsRnz/30-check-campaignexpired-before-displaying-any-new-campaign-tasks-to-any-user)
        total_reward: Optional[ProjectMoney] = self.tasks \
            .filter(task_status__interacted=True) \
            .aggregate(total_reward=Sum('reward'))['total_reward']
        return (
            self.finished_at <= n
            or (total_reward and total_reward > self.budget)
        )

    def start(self, dt=None):
        self.started_at = dt if dt else now()
        self.save(update_fields={'started_at'})

    def finish(self, dt=None):
        self.finished_at = dt if dt else now()
        self.save(update_fields={'finished_at'})

    def __str__(self):
        return f"{ActiveInactiveStatus(self.status).label} " \
               f"{self.budget} " \
               f"\"{self.name}\" " \
               f"(#{self.pk})"
