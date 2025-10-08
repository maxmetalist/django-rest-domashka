from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


@shared_task
def send_course_update_notification(course_id, updated_lesson_title=None):
    """
    Задача для отправки уведомлений об обновлении курса подписчикам
    """
    # Ленивые импорты спецом сюда внесены, чтобы избежать циклизации
    from materials.models import Subscription, Course
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course).select_related("user")

        if not subscriptions:
            return f"Нет подписанных аленей на курс: {course.title}"

        subject = f"Курс '{course.title}' обновлен!"

        if updated_lesson_title:
            message = f"""
            Здорово, бро!

            В курсе "{course.title}" был обновлен урок: "{updated_lesson_title}".
            Такая вот фигня!

            Сгоняй вот сюда, чтобы позырить, что там наваяли:
            {getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/courses/{course.id}/

            Понравится, ну приколдесно!
            Не понравится, ну облом...
            
            Это был Масяма, удачи тебе!
            """
        else:
            message = f"""
            Здорово, бро!

            Такое дело, тут курс "{course.title}" был обновлен.

            Сгоняй сюда, чтобы позырить, что там наваяли:
            {getattr(settings, "FRONTEND_URL", "http://localhost:3000")}/courses/{course.id}/

            Понравится, ну приколдесно!
            Не понравится, ну облом...
            
            Это был Масяма, удачи тебе!
            """

        email_list = [subscription.user.email for subscription in subscriptions]

        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=email_list,
            fail_silently=False,
        )

        return f"Отправка письма об обновлении {len(email_list)} юзерам, подписанным на курс: {course.title}"

    except Course.DoesNotExist:
        return f"Курс с id {course_id} не существует"
    except Exception as e:
        return f"Ошибка отправки уведомления: {str(e)}"


@shared_task
def deactivate_inactive_users():
    """
    Задача для деактивации пользователей, которые не заходили более месяца
    """
    # ленивые импорты спецом внесены сюда, чтобы избежать циклизации
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        # Вычисляем дату (30 дней назад)
        threshold_date = timezone.now() - timedelta(days=30)

        # Находим пользователей, которые не заходили более месяца и еще активны
        inactive_users = User.objects.filter(last_login__lt=threshold_date, is_active=True)

        count_before = inactive_users.count()

        # Деактивируем пользователей
        deactivated_count = inactive_users.update(is_active=False)

        # Логируем результат
        result = f"Деактивировано {deactivated_count} пользователей из {count_before} неактивных"
        print(f"✅ {result}")

        return result

    except Exception as e:
        error_msg = f"Ошибка при деактивации пользователей: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg
