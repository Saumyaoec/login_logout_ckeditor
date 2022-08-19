import pytz
import unicodedata
import uuid
from django.utils.encoding import force_text
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import ugettext_lazy as _


class AppUserManager(BaseUserManager):

    def _create_user(self, email, first_name, last_name, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('User must have an email address')
        email = self.normalize_email(email)
        first_name = self.normalize_firstname(first_name)
        last_name = self.normalize_lastname(last_name)
        user = self.model(email=email, first_name=first_name,
                          last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, first_name=None, last_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, first_name, last_name, password, **extra_fields)

    @classmethod
    def normalize_firstname(cls, first_name):
        return unicodedata.normalize('NFKC', force_text(first_name))

    @classmethod
    def normalize_lastname(cls, last_name):
        return unicodedata.normalize('NFKC', force_text(last_name))


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=254, blank=True)
    last_name = models.CharField(max_length=254, blank=True)
    email = models.EmailField(blank=True, unique=True)
    username = models.UUIDField(default=uuid.uuid4, editable=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    # REQUIRED_FIELDS = ['username', 'address1', 'address2', 'area_code', 'country_code']

    objects = AppUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_absolute_url(self):
        return "/account/profile/"

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def get_avatar(self):
        # "Returns the short name for the user."
        return Profile.objects.get(user=self).avatar.url


def user_avatar_dir(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'uploads/user_{0}/avatar/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    GENDER = (
        (MALE, 'male'),
        (FEMALE, 'female'),
    )
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_avatar_dir)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    timezone = models.CharField(
        max_length=32, choices=TIMEZONES, default='UTC')
    gender = models.CharField(max_length=1, choices=GENDER, blank=True)
    email_verified = models.BooleanField(default=False)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    google_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
