import stripe
from django.conf import settings
from django.core.exceptions import ValidationError

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    @staticmethod
    def create_product(name, description):
        """Создание продукта в Stripe"""
        try:
            product = stripe.Product.create(name=name, description=description)
            return product
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe error: {e}")

    @staticmethod
    def create_price(product_id, amount, currency="usd"):
        """Создание цены в Stripe"""
        try:
            # Конвертируем в центы (Stripe работает с копейками)
            amount_in_cents = int(amount * 100)

            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_in_cents,
                currency=currency,
            )
            return price
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe error: {e}")

    @staticmethod
    def create_checkout_session(price_id, success_url, cancel_url, metadata=None):
        """Создание сессии оплаты"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            return session
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe error: {e}")

    @staticmethod
    def get_session(session_id):
        """Получение информации о сессии"""
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe error: {e}")
