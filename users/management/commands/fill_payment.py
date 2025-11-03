from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Создает тестовые платежи"

    def handle(self, *args, **options):
        # Получаем первого пользователя, курс и урок
        user = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR("Нет пользователей в базе данных"))
            return

        payments_data = [
            {"user": user, "paid_course": course, "paid_lesson": None, "amount": 10000, "payment_method": "transfer"},
            {"user": user, "paid_course": None, "paid_lesson": lesson, "amount": 2500, "payment_method": "cash"},
            {"user": user, "paid_course": course, "paid_lesson": None, "amount": 15000, "payment_method": "transfer"},
        ]

        for payment_data in payments_data:
            payment, created = Payment.objects.get_or_create(**payment_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан платеж: {payment.user.email} - {payment.amount} руб."))
            else:
                self.stdout.write(self.style.WARNING(f"Платеж уже существует: {payment}"))
