from django_cron import CronJobBase, Schedule
from referral_project.users.models import User
from referral_project.users.fields import ActivatedDeactivatedStatus
from django.conf import settings
from django.utils.timezone import now

class UserActivationCronJob(CronJobBase):
    RUN_EVERY_MINS = settings.TASK_CRON_DURATION # every 24hrs
    RUN_AT_TIMES = [settings.TASK_CRON_START_TIME]

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'referral_project.users.cron.user_activation_cron_job'    # a unique code

    def do(self):
        dt = now()
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        User.objects.filter(
            status=ActivatedDeactivatedStatus.ACTIVATED,
            expiration_date__range=(start, end)
        ).update(status=ActivatedDeactivatedStatus.DEACTIVATED)
