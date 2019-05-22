from rest_framework.routers import DefaultRouter

from referral_project.transactions.api.v0.views import Transactions

router = DefaultRouter()

router.register(r'transactions', Transactions)

urlpatterns = router.urls
