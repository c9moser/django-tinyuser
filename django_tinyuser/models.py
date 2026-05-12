from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TinyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        if not username:
            raise ValueError(_('The Username field must be set'))
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)


class TinyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        db_column='email_address',
        verbose_name=_('email address')
    )
    username = models.CharField(
        max_length=127,
        unique=True,
        db_column='username',
        verbose_name=_('username')
    )
    is_active = models.BooleanField(
        default=True,
        db_column='is_active',
        verbose_name=_('active')
    )
    is_staff = models.BooleanField(
        default=False,
        db_column='is_staff',
        verbose_name=_('staff status')
    )
    is_superuser = models.BooleanField(
        default=False,
        db_column='is_superuser',
        verbose_name=_('superuser status')
    )
    is_verified = models.BooleanField(
        default=False,
        db_column='is_verified',
        verbose_name=_('verified')
    )

    joined_at = models.DateTimeField(
        default=timezone.now,
        db_column='joined_at',
        verbose_name=_('joined at')
    )

    objects = TinyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def display_name(self):
        self.profile = getattr(self, 'profile', None)
        if not self.profile and self.id:
            try:
                self.profile = TinyUserProfile.objects.filter(user_id=self.id).first()
            except TinyUserProfile.DoesNotExist:
                self.profile = TinyUserProfile.objects.create(user=self,
                                                              first_name='',
                                                              last_name='',
                                                              bio='')

        if self.profile:
            if (self.profile.first_name or self.profile.last_name):
                return f"{self.profile.first_name} {self.profile.last_name}".strip()
            elif self.profile.first_name:
                return self.profile.first_name
            elif self.profile.last_name:
                return self.profile.last_name
        return self.username

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

        db_table = 'tinyuser'

        indexes = [
            models.Index(fields=['email'], name='email_idx'),
            models.Index(fields=['username'], name='username_idx'),
        ]


class TinyUserProfile(models.Model):
    user = models.OneToOneField(
        TinyUser,
        on_delete=models.CASCADE,
        related_name='profile')
    first_name = models.CharField(
        max_length=30,
        blank=True,

    )
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

        db_table = 'tinyuser_profile'
