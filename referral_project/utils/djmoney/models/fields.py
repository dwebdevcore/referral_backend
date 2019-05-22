from functools import partial

from django.conf import settings
from djmoney.models.fields import MoneyField
from djmoney.money import Money

ProjectMoneyField = partial(
    MoneyField,
    max_digits=10,
    decimal_places=2,
)

ProjectMoney = partial(
    Money,
    currency=settings.DEFAULT_CURRENCY
)
