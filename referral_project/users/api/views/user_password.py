from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from referral_project.users.api.serializers import UserPasswordResetSerializer, UserPasswordResetConfirmSerializer

sensitive_post_parameters_d = method_decorator(sensitive_post_parameters(
    'password', 'old_password', 'new_password1', 'new_password2'
))


class UserPasswordResetView(GenericAPIView):
    serializer_class = UserPasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            data={'detail': _("Password reset e-mail has been sent.")},
            status=HTTP_200_OK,
        )


class UserPasswordResetConfirmView(GenericAPIView):
    serializer_class = UserPasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    @sensitive_post_parameters_d
    def dispatch(self, *args, **kwargs):
        return super(UserPasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update(kwargs)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            data={'detail': _("Password has been reset.")},
            status=HTTP_200_OK,
        )
