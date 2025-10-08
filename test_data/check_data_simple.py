import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from materials.models import Course, Subscription

User = get_user_model()


def check_existing_data():
    """Проверяем существующие данные"""
    print("📊 Проверяем существующие данные...")

    # Пользователи
    users = User.objects.all()
    print(f"👥 Всего пользователей: {users.count()}")
    for user in users:
        print(f"  - {user.email} (ID: {user.id})")

    # Курсы
    courses = Course.objects.all()
    print(f"📚 Всего курсов: {courses.count()}")
    for course in courses:
        subs = Subscription.objects.filter(course=course)
        print(f"  - '{course.title}' (ID: {course.id}) - подписчиков: {subs.count()}")

    # Подписки
    subscriptions = Subscription.objects.all().select_related("user", "course")
    print(f"📧 Всего подписок: {subscriptions.count()}")
    for sub in subscriptions:
        print(f"  - {sub.user.email} -> '{sub.course.title}'")


if __name__ == "__main__":
    check_existing_data()
