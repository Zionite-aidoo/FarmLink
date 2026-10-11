from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
import re

from .models import OTPCode
from .services import normalize_phone, request_otp, verify_otp

import sys

is_dev = settings.DEBUG or 'test' in sys.argv

User = get_user_model()


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next', '')
    safe_next = next_url if url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()) else ''
    if request.method == 'POST' and request.POST.get('action') == 'request':
        phone = normalize_phone(request.POST.get('phone'))
        mode = request.POST.get('mode', 'login')
        if not re.fullmatch(r'\+[1-9]\d{7,14}', phone):
            messages.error(request, 'Enter a valid phone number, including the country code.')
        else:
            user = User.objects.filter(phone=phone, is_active=True).first()
            if mode == 'register':
                full_name = request.POST.get('full_name', '').strip()
                role = request.POST.get('role', User.Role.BUYER)
                if user:
                    messages.error(request, 'This phone number already has an account. Choose Sign in instead.')
                elif not full_name or role not in {User.Role.BUYER, User.Role.FARMER, User.Role.BOTH}:
                    messages.error(request, 'Enter your name and choose a valid account type.')
                else:
                    try:
                        record = request_otp(phone, OTPCode.Purpose.REGISTER, {'full_name': full_name[:120], 'role': role})
                        request.session['otp_phone'] = phone
                        request.session['otp_next'] = safe_next
                        if is_dev:
                            request.session['dev_otp_hint'] = getattr(record, 'plain_code', '')
                        messages.success(request, 'A one-time code has been sent. Check the development server console.')
                        return redirect('accounts:verify')
                    except ValueError as error:
                        messages.error(request, str(error))
                    except RuntimeError as error:
                        messages.error(request, str(error))
            elif user:
                try:
                    record = request_otp(phone, OTPCode.Purpose.LOGIN)
                    request.session['otp_phone'] = phone
                    request.session['otp_next'] = safe_next
                    if is_dev:
                        request.session['dev_otp_hint'] = getattr(record, 'plain_code', '')
                    messages.success(request, 'A one-time code has been sent. Check the development server console.')
                    return redirect('accounts:verify')
                except (ValueError, RuntimeError) as error:
                    messages.error(request, str(error))
            else:
                messages.info(request, f'No account was found for {phone}. Please register below to get started.')
                return redirect(f"{reverse('accounts:login')}?mode=register&phone={phone}")
        return render(request, 'accounts/login.html', {'next': safe_next, 'mode': mode, 'phone': phone})
    mode = 'register' if request.GET.get('mode') == 'register' else 'login'
    phone = request.GET.get('phone', '')
    return render(request, 'accounts/login.html', {'next': safe_next, 'mode': mode, 'phone': phone})


def verify_view(request):
    phone = request.session.get('otp_phone')
    if not phone:
        messages.info(request, 'Request a sign-in code first.')
        return redirect('accounts:login')
    if request.method == 'POST':
        code = ''.join(ch for ch in request.POST.get('code', '') if ch.isdigit())
        record = OTPCode.objects.filter(phone=phone, consumed_at__isnull=True).first()
        if not record or not verify_otp(record, code):
            messages.error(request, 'That code is invalid or expired. Request a new code if needed.')
            return render(request, 'accounts/verify.html', {'phone': phone})
        with transaction.atomic():
            if record.purpose == OTPCode.Purpose.REGISTER:
                data = record.registration_data
                user, created = User.objects.get_or_create(
                    phone=phone,
                    defaults={
                        'full_name': data.get('full_name', ''),
                        'role': data.get('role', User.Role.BUYER),
                        'is_phone_verified': True,
                    },
                )
                if created:
                    user.set_unusable_password()
                    user.save(update_fields=['password'])
                if not created:
                    messages.error(request, 'An account already exists for this number. Please sign in.')
                    request.session.pop('otp_phone', None)
                    return redirect('accounts:login')
            else:
                user = User.objects.filter(phone=phone, is_active=True).first()
                if not user:
                    messages.error(request, 'No active account was found. Please register first.')
                    return redirect('accounts:login')
                user.is_phone_verified = True
                user.save(update_fields=['is_phone_verified'])
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.session.pop('otp_phone', None)
        request.session.pop('dev_otp_hint', None)
        next_url = request.session.pop('otp_next', '')
        if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect('dashboard:home')
    dev_otp_hint = request.session.get('dev_otp_hint') if is_dev else ''
    return render(request, 'accounts/verify.html', {'phone': phone, 'dev_otp_hint': dev_otp_hint})


@require_POST
def resend_view(request):
    phone = request.session.get('otp_phone')
    if not phone:
        return redirect('accounts:login')
    previous = OTPCode.objects.filter(phone=phone).first()
    purpose = previous.purpose if previous else OTPCode.Purpose.LOGIN
    registration_data = previous.registration_data if previous and purpose == OTPCode.Purpose.REGISTER else None
    try:
        record = request_otp(phone, purpose, registration_data)
        if is_dev:
            request.session['dev_otp_hint'] = getattr(record, 'plain_code', '')
        messages.success(request, 'A new one-time code has been sent. Check the development server console.')
    except (ValueError, RuntimeError) as error:
        messages.error(request, str(error))
    return redirect('accounts:verify')


@require_POST
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('core:home')
