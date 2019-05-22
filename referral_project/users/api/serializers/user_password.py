from typing import Dict, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.fields import EmailField, CharField
from rest_framework.serializers import Serializer

__all__ = [
    'UserPasswordResetSerializer',
    'UserPasswordResetConfirmSerializer',
]

User = get_user_model()
password_field_max_length = 128


class UserPasswordResetSerializer(Serializer):
    email = EmailField()
    password_reset_form_class = PasswordResetForm

    def validate_email(self, value: str):
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise ValidationError(self.reset_form.errors)
        return value

    def save(self):
        request = self.context.get('request')
        self.reset_form.save(**{
            'request': request,
            'use_https': request.is_secure(),
            'from_email': settings.DEFAULT_FROM_EMAIL,
        })


class UserPasswordResetConfirmSerializer(Serializer):
    new_password1 = CharField(max_length=password_field_max_length)
    new_password2 = CharField(max_length=password_field_max_length)
    uidb64 = CharField()
    token = CharField()

    set_password_form_class = SetPasswordForm

    def validate(self, attrs: Dict[str, Any]):
        uidb64 = attrs.get('uidb64')
        token = attrs.get('token')

        try:
            pk = int(force_text(urlsafe_base64_decode(uidb64)))
            user = User.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError):
            raise ValidationError({'uidb64': _("Invalid value.")})
        except User.DoesNotExist:
            raise ValidationError({'uidb64': _("User does not exist.")})

        self.set_password_form = self.set_password_form_class(user=user, data=attrs)
        if not self.set_password_form.is_valid():
            raise ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(user, token):
            raise ValidationError({'token': _("Invalid value.")})

        return attrs

    def save(self):
        return self.set_password_form.save()
