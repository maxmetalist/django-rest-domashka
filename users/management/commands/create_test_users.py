from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Создает тестовых пользователей"

    def handle(self, *args, **options):
        users_data = [
            {"email": "user1@example.com", "password": "12345"},
            {"email": "user2@example.com", "password": "12345"},
            {"email": "user3@example.com", "password": "12345"},
            {"email": "student@example.com", "password": "12345"},
            {"email": "teacher@example.com", "password": "12345"},
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data["email"], defaults={"password": user_data["password"]}
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Создан пользователь: {user.email}"))
            else:
                self.stdout.write(self.style.WARNING(f"Пользователь уже существует: {user.email}"))
