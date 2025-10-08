import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from materials.tasks import send_course_update_notification


def test_basic():
    """Простой тест задачи"""
    print("🧪 Тестируем базовую функциональность задачи...")

    try:
        # Тестируем синхронно (без Celery)
        result = send_course_update_notification(1, "Тестовый урок")
        print(f"✅ Синхронный результат: {result}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    test_basic()
