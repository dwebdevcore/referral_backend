from rest_framework.routers import DefaultRouter

from referral_project.wallets.api.v0.views import Wallets

router = DefaultRouter()

router.register(r'wallets', Wallets, base_name='wallets')

urlpatterns = router.urls
