from django_cron import CronJobBase, Schedule
from referral_project.tasks.models import TaskStatus
from referral_project.campaigns.models import Campaign
from django.conf import settings
from django.utils.timezone import now

class TaskCronJob(CronJobBase):
    RUN_EVERY_MINS = settings.TASK_CRON_DURATION # every 24hrs
    RUN_AT_TIMES = [settings.TASK_CRON_START_TIME]

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'referral_project.tasks.cron.task_cron_job'    # a unique code

    def do(self):
        TaskStatus.objects.filter(interacted=True).update(interacted=False)
        dt = now()
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        for campaign in Campaign.objects.filter(finished_at__range=(start, end)).all():
            campaign.tasks.update(expired=True)
