from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from referral_project.users.api.views import UserViewSet
from referral_project.users.api.views.user_password import UserPasswordResetView, UserPasswordResetConfirmView

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='users')

urlpatterns = [
    url(r'', include(router.urls)),
    url(
        regex=r'^users/password/reset/$',
        view=UserPasswordResetView.as_view(),
        name='password_reset',
    ),
    url(
        regex=r'^users/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=UserPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
]
