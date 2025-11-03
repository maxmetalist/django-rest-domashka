from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson


class Command(BaseCommand):
    help = "Создает группы пользователей с соответствующими правами"

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderators_group, created = Group.objects.get_or_create(name="moderators")

        if created:
            # Получаем права для курсов
            course_content_type = ContentType.objects.get_for_model(Course)
            course_view_permission = Permission.objects.get(content_type=course_content_type, codename="view_course")
            course_change_permission = Permission.objects.get(
                content_type=course_content_type, codename="change_course"
            )

            # Получаем права для уроков
            lesson_content_type = ContentType.objects.get_for_model(Lesson)
            lesson_view_permission = Permission.objects.get(content_type=lesson_content_type, codename="view_lesson")
            lesson_change_permission = Permission.objects.get(
                content_type=lesson_content_type, codename="change_lesson"
            )

            # Добавляем права в группу
            moderators_group.permissions.add(
                course_view_permission, course_change_permission, lesson_view_permission, lesson_change_permission
            )

            self.stdout.write(
                self.style.SUCCESS('Группа "moderators" создана с правами просмотра и изменения курсов и уроков')
            )
        else:
            self.stdout.write(self.style.WARNING('Группа "moderators" уже существует'))
