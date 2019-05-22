from rest_framework.routers import DefaultRouter

from referral_project.payment_method.api.v0.views import PaymentMethods

router = DefaultRouter()

router.register(r'payment_methods', PaymentMethods, base_name='PaymentMethods')

urlpatterns = router.urls
