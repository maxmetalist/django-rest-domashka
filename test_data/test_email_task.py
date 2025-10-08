import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from materials.tasks import send_course_update_notification
from materials.models import Course


def test_email_task():
    """Тестируем задачу отправки писем"""
    print("🧪 Тестируем задачу отправки уведомлений...")

    # Найдем курс с подписчиками
    courses_with_subs = Course.objects.filter(subscriptions__isnull=False).distinct()

    if not courses_with_subs.exists():
        print("❌ Нет курсов с подписчиками. Сначала создайте подписки.")
        return

    course = courses_with_subs.first()
    subs_count = course.subscriptions.count()

    print(f"📚 Тестируем на курсе: '{course.title}'")
    print(f"👥 Подписчиков: {subs_count}")

    # Тест 1: Синхронное выполнение
    print("\n1. 🔄 Синхронный тест:")
    try:
        result = send_course_update_notification(course.id, "Тестовый урок по основам")
        print(f"✅ Результат: {result}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    # Тест 2: Асинхронное выполнение через Celery
    print("\n2. ⚡ Асинхронный тест через Celery:")
    try:
        task = send_course_update_notification.delay(course.id, "Асинхронное обновление")
        print(f"📋 Задача отправлена в Celery! ID: {task.id}")
        print(f"📊 Начальный статус: {task.status}")

        # Ждем завершения задачи
        print("⏳ Ожидаем выполнение...")
        for i in range(10):
            if task.ready():
                result = task.get()
                status = task.status
                print(f"🎉 Задача завершена!")
                print(f"📊 Статус: {status}")
                print(f"📨 Результат: {result}")
                break
            else:
                print(f"🔄 Задача выполняется... ({i + 1}/10)")
                time.sleep(2)
        else:
            print("⏰ Время ожидания истекло")

    except Exception as e:
        print(f"❌ Ошибка при асинхронном выполнении: {e}")


if __name__ == "__main__":
    test_email_task()
