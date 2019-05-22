from django.db.models import CASCADE, ForeignKey, CharField
from referral_project.payment_method.fields import PaymentMethodOptionField, PaymentMethodOption
from referral_project.utils.djmoney.models.fields import ProjectMoneyField
from model_utils.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from referral_project.utils.djmoney.models.fields import ProjectMoney


class PaymentMethod(TimeStampedModel):
    class Meta:
        verbose_name = _("PaymentMethod")
        verbose_name_plural = _("PaymentMethods")

    name = CharField(max_length=30, null=True, verbose_name='Payment Method Name')
    option = PaymentMethodOptionField()
    min_deposit_amount = ProjectMoneyField(default=ProjectMoney(amount=0), verbose_name='Minimum Deposit Amount')

    def __str__(self):
        return f"{self.name} " \
               f" for {PaymentMethodOption(self.option).label} " \


class PaymentInformation(TimeStampedModel):
    class Meta:
        verbose_name = _("PaymentInformation")
        verbose_name_plural = _("PaymentInformation")

    email = CharField(max_length=30, null=True, blank=True, verbose_name='Payment Email Address')
    payment_method = ForeignKey(
        PaymentMethod,
        on_delete=CASCADE,
        related_name='payment_information',
    )

    def __str__(self):
        return f"{self.email} " \
               f" : {self.payment_method} " \
