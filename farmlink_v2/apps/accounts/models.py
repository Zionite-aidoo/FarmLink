import re
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, full_name, password=None, **extra_fields):
        if not phone:
            raise ValueError('A phone number is required.')
        user = self.model(phone=self.normalize_phone(phone), full_name=full_name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    @staticmethod
    def normalize_phone(phone):
        phone = ''.join(character for character in phone.strip() if character.isdigit() or character == '+')
        if phone.startswith('0') and len(phone) == 10:
            phone = '+233' + phone[1:]
        elif phone.startswith('233') and len(phone) == 12:
            phone = '+' + phone
        elif not phone.startswith('+'):
            phone = '+' + phone
        if not re.fullmatch(r'\+[1-9]\d{7,14}', phone):
            raise ValueError('Phone numbers must be valid international numbers, for example +233241234567.')
        return phone

    def create_user(self, phone, full_name='', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, full_name, password, **extra_fields)

    def create_superuser(self, phone, full_name='', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not extra_fields['is_staff'] or not extra_fields['is_superuser']:
            raise ValueError('A superuser must have staff and superuser permissions.')
        return self._create_user(phone, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        BUYER = 'buyer', 'Buyer'
        FARMER = 'farmer', 'Farmer'
        BOTH = 'both', 'Buyer and farmer'

    phone = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=120)
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.BUYER)
    region = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.phone})'

    @property
    def can_sell(self):
        return self.role in {self.Role.FARMER, self.Role.BOTH}


class OTPCode(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = 'login', 'Login'
        REGISTER = 'register', 'Registration'

    phone = models.CharField(max_length=20, db_index=True)
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=12, choices=Purpose.choices)
    registration_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_usable(self):
        return self.consumed_at is None and self.expires_at > timezone.now() and self.attempts < 5
