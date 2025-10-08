from django.db.models.signals import post_save
from django.dispatch import receiver
from materials.models import Lesson
from materials.tasks import send_course_update_notification
from .utils import should_send_notification


@receiver(post_save, sender=Lesson)
def check_course_update_notification(sender, instance, created, **kwargs):
    """
    Сигнал для проверки и отправки уведомлений при обновлении уроков
    """
    if not created:  # Только при обновлении существующих уроков
        course = instance.course

        # Проверяем, нужно ли отправлять уведомление
        if should_send_notification(course, threshold_hours=4):
            # Отправляем задачу в Celery
            send_course_update_notification.delay(course_id=course.id, updated_lesson_title=instance.title)
