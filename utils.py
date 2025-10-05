from django.utils import timezone
from datetime import timedelta


def should_send_notification(course, threshold_hours=4):
    """
    Проверяет, нужно ли отправлять уведомление об обновлении курса.
    Возвращает True, если курс не обновлялся более threshold_hours часов
    """
    if not course.updated_at:
        return True

    time_diff = timezone.now() - course.updated_at
    return time_diff > timedelta(hours=threshold_hours)
