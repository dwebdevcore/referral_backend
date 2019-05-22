from rest_framework.routers import DefaultRouter

from referral_project.choices.api.v0.views import Choices

router = DefaultRouter()

router.register(r'choices', Choices, base_name='choices')

urlpatterns = router.urls
