from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import (
    EmailField, ManyToManyField, ForeignKey, CASCADE, CharField, ImageField, DateTimeField)
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from referral_project.tasks.models import Task, TaskStatus
from referral_project.users.fields import ActivatedDeactivatedStatusField, IDKindField
from referral_project.utils.django.fields import generate_upload_to


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


def get_user_identification_upload_to(
    instance: settings.AUTH_USER_MODEL,
    filename: str,
) -> str:
    return generate_upload_to(
        settings.USER_IDENTIFICATION_MEDIA_DIR_PATH,
        instance,
        filename
    )


class User(AbstractUser):
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = (("can_view_only", "View only data"),)

    email = EmailField(
        unique=True,
        verbose_name=_('Email'),
    )
    status = ActivatedDeactivatedStatusField()
    tasks = ManyToManyField(
        Task,
        related_name='users',
        through=TaskStatus,
    )
    referrer = ForeignKey(
        'self',
        null=True, blank=True,
        related_name='referrals',
        on_delete=CASCADE,
    )
    address = CharField(
        max_length=255,
        blank=True
    )
    country = CharField(
        max_length=255,
        blank=True
    )
    city = CharField(
        max_length=255,
        blank=True
    )
    phone = PhoneNumberField(blank=True)
    customer = ForeignKey(
        'KYC',
        null=True, blank=True,
        related_name='users',
        on_delete=CASCADE,
    )
    activation_date = DateTimeField(blank=True, null=True)
    expiration_date = DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} (#{self.pk})"

    def referral_link(self, request):
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'

        return f"{protocol}://{domain}{settings.REACT_REGISTER_URL}{self.pk}"


class KYC(TimeStampedModel):
    class Meta:
        verbose_name = _("KYC")
        verbose_name_plural = _("KYC")
        permissions = (("can_view_only", "View only data"),)

    first_name = CharField(
        _('first name'),
        max_length=30,
        blank=True
    )
    last_name = CharField(
        _('last name'),
        max_length=30,
        blank=True
    )
    address = CharField(
        max_length=255,
        blank=True
    )
    country = CharField(
        max_length=255,
        blank=True
    )
    city = CharField(
        max_length=255,
        blank=True
    )
    phone = PhoneNumberField(blank=True)
    identification = CharField(
        max_length=255,
        blank=True
    )
    id_kind = IDKindField()

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"(#{self.pk})"
