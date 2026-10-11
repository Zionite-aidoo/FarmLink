import logging

from django.conf import settings

logger = logging.getLogger('farmlink.sms')


class SMSBackend:
    def send_otp(self, phone, code):
        raise NotImplementedError


import sys

class ConsoleSMSBackend(SMSBackend):
    def send_otp(self, phone, code):
        if not settings.DEBUG and 'test' not in sys.argv:
            raise RuntimeError('The console SMS backend is restricted to local development.')
        logger.info('FarmLink development OTP for %s: %s (expires in 10 minutes)', phone, code)
        print(f"\n{'='*55}\n [FARMLINK DEV OTP] Phone: {phone} | Code: {code}\n{'='*55}\n", flush=True)


class UnconfiguredSMSBackend(SMSBackend):
    provider_name = 'selected'

    def send_otp(self, phone, code):
        raise RuntimeError(f'The {self.provider_name} SMS adapter is not configured yet.')


def get_sms_backend():
    if settings.SMS_BACKEND == 'console':
        return ConsoleSMSBackend()
    if settings.SMS_BACKEND in {'hubtel', 'mnotify', 'africas_talking'}:
        backend = UnconfiguredSMSBackend()
        backend.provider_name = settings.SMS_BACKEND.replace('_', ' ')
        return backend
    return UnconfiguredSMSBackend()
