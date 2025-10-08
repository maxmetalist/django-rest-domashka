import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from materials.models import Course, Subscription

User = get_user_model()


def create_test_subscriptions():
    """Создаем тестовые подписки"""
    print("🎯 Создаем тестовые подписки...")

    # Получаем существующих пользователей
    users = User.objects.all()[:3]  # Берем первых трех пользователей
    courses = Course.objects.all()

    created_count = 0

    for user in users:
        for course in courses:
            # Создаем подписку для каждого пользователя на каждый курс
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                course=course
            )

            if created:
                created_count += 1
                print(f"✅ Создана подписка: {user.email} -> '{course.title}'")

    print(f"\n🎉 Всего создано подписок: {created_count}")

    # Покажем итоговую статистику
    print("\n📊 Итоговая статистика:")
    for course in courses:
        subs_count = Subscription.objects.filter(course=course).count()
        print(f"  - '{course.title}': {subs_count} подписчиков")


if __name__ == "__main__":
    create_test_subscriptions()
