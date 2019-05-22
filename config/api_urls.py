from django.conf.urls import url, include
from rest_framework.authtoken.views import obtain_auth_token

from referral_project.campaigns.api.v0.urls import router as campaigns_router
from referral_project.tasks.api.v0.urls import router as tasks_router
from referral_project.transactions.api.v0.urls import router as transactions_router
from referral_project.users.api.urls import router as users_router
from referral_project.utils.rest_framework.routers import ExtendableDefaultRouter
from referral_project.wallets.api.v0.urls import router as wallets_router
from referral_project.choices.api.v0.urls import router as choices_router
from referral_project.payment_method.api.v0.urls import router as payment_method_router

urlpatterns = [
    url(r'^obtain-auth-token/$', obtain_auth_token),
]

router = ExtendableDefaultRouter()
router.extend(users_router)
router.extend(campaigns_router)
router.extend(tasks_router)
router.extend(wallets_router)
router.extend(transactions_router)
router.extend(choices_router)
router.extend(payment_method_router)

urlpatterns += [
    url(r'^v0/', include(router.urls)),
]
