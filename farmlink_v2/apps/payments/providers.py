from dataclasses import dataclass
from secrets import token_hex

from django.conf import settings
from django.utils import timezone


@dataclass(frozen=True)
class PaymentResult:
    status: str
    reference: str
    paid_at: object = None
    callback: dict | None = None


import sys


class SimulatedMoMoProvider:
    """Local-only payment adapter. It never contacts a real payment network."""

    def initiate(self, payment):
        if not (settings.DEBUG or 'test' in sys.argv) or settings.PAYMENTS_MODE != 'simulated':
            raise RuntimeError('Simulated payments are available only in local development.')
        return PaymentResult(
            status='success',
            reference='SIM-' + token_hex(6).upper(),
            paid_at=timezone.now(),
            callback={'mode': 'simulated', 'approved': True},
        )


def get_momo_provider():
    if settings.PAYMENTS_MODE == 'simulated' and (settings.DEBUG or 'test' in sys.argv):
        return SimulatedMoMoProvider()
    raise RuntimeError('No live Mobile Money provider is configured.')
