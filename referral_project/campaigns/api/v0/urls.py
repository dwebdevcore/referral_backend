from rest_framework.routers import DefaultRouter

from referral_project.campaigns.api.v0.views import Campaigns

router = DefaultRouter()

router.register(r'campaigns', Campaigns)

urlpatterns = router.urls
