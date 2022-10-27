import os
import uuid

from django.contrib.auth import get_user_model
from django.conf import settings

from yookassa import Configuration
from yookassa import Payment as YooPayment

from .models import Payment

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")

User = get_user_model()


def create_payment(user: User, value: int):
    """
    Create `PaymentResponse` object
    """

    res = YooPayment.create(
        {
            "capture": True,
            "amount": {
                "value": value,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": settings.PAYMENT_REDIRECT_URL
            },
            "decription": "Подписка на приложение",
            "metadata": {
                "userID": user.id
            }
        },
        uuid.uuid4()
    )

    Payment.objects.create(
        user=user,
        payment_id=res.id,
        created_at=res.created_at
    )

    return res
