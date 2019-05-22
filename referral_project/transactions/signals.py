from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver
from referral_project.transactions.fields import Action
from referral_project.utils.django.fields import ProcessStatus

from referral_project.transactions.models import Transaction, Deposit, Withdraw


@receiver(post_save, sender=Transaction)
@receiver(post_save, sender=Withdraw)
@receiver(post_save, sender=Deposit)
def balance_wallets(instance: Transaction, created: bool, **kwargs):
    with atomic():
        amount = instance.amount
        sender = instance.sender
        receiver_ = instance.receiver

        if instance.action == Action.WITHDRAW or instance.action == Action.DEPOSIT:
            if instance.status == ProcessStatus.COMPLETED:
                sender.balance -= amount
                sender.save(update_fields={'balance'})
                receiver_.balance += amount
                receiver_.save(update_fields={'balance'})
        else:
            sender.balance -= amount
            sender.save(update_fields={'balance'})
            receiver_.balance += amount
            receiver_.save(update_fields={'balance'})
