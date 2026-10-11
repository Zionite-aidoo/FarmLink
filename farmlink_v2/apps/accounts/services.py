import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.utils import timezone

from .models import OTPCode, User
from .sms import get_sms_backend


def normalize_phone(value):
    value = ''.join(ch for ch in (value or '').strip() if ch.isdigit() or ch == '+')
    if value.startswith('0') and len(value) == 10:
        value = '+233' + value[1:]
    elif value.startswith('233') and len(value) == 12:
        value = '+' + value
    if not value.startswith('+'):
        value = '+' + value
    return value


def request_otp(phone, purpose, registration_data=None):
    sms_backend = get_sms_backend()
    throttle_key = 'farmlink-otp:' + hashlib.sha256(phone.encode()).hexdigest()
    last_sent = cache.get(throttle_key)
    if last_sent and (timezone.now() - last_sent).total_seconds() < 60:
        raise ValueError('Please wait one minute before requesting another code.')
    count_key = throttle_key + ':hour'
    attempts = cache.get(count_key, 0)
    if attempts >= 5:
        raise ValueError('Too many code requests. Try again later.')

    code = f'{secrets.randbelow(1_000_000):06d}'
    now = timezone.now()
    if OTPCode.objects.filter(phone=phone, created_at__gte=now - timedelta(minutes=1)).exists():
        raise ValueError('Please wait one minute before requesting another code.')
    if OTPCode.objects.filter(phone=phone, created_at__gte=now - timedelta(hours=1)).count() >= 5:
        raise ValueError('Too many code requests. Try again later.')
    OTPCode.objects.filter(phone=phone, consumed_at__isnull=True).update(consumed_at=now)
    record = OTPCode.objects.create(
        phone=phone,
        code_hash=make_password(code),
        purpose=purpose,
        registration_data=registration_data or {},
        expires_at=now + timedelta(minutes=10),
    )
    cache.set(throttle_key, now, 60)
    cache.set(count_key, attempts + 1, 3600)
    sms_backend.send_otp(phone, code)
    record.plain_code = code
    return record


def verify_otp(record, code):
    if not record.is_usable:
        return False
    record.attempts += 1
    valid = check_password(code, record.code_hash)
    if valid:
        record.consumed_at = timezone.now()
    record.save(update_fields=['attempts', 'consumed_at'])
    return valid
