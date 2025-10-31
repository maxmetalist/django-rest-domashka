import os

import django
from materials.tasks import send_course_update_notification

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Тестируем задачу
try:
    result = send_course_update_notification.delay(1, "Test Lesson")
    print(f"Задача отправлена! ID: {result.id}")
    print(f"Статус задачи: {result.status}")
except Exception as e:
    print(f"Ошибка: {e}")
