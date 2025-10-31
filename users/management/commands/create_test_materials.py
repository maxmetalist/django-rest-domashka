from django.core.management.base import BaseCommand

from materials.models import Course, Lesson


class Command(BaseCommand):
    help = "Создает тестовые курсы и уроки"

    def handle(self, *args, **options):
        # Создаем курсы
        courses_data = [
            {"title": "Python для чайников", "description": "К чёрту всё, будем гамать скайрим"},
            {"title": "Django лошпетам", "description": "Надоел скайрим? Ну давайте StarCraft-2"},
            {"title": "JavaScript", "description": "Основы JavaScript для таких дураков, как я"},
        ]

        created_courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(title=course_data["title"], defaults=course_data)
            if created:
                created_courses.append(course)
                self.stdout.write(self.style.SUCCESS(f"Создан курс: {course.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Курс уже существует: {course.title}"))

        # Создаем уроки
        lessons_data = [
            {
                "title": "Введение в Python",
                "description": "Как не охренеть с первого урока и не поехать крышей",
                "course": created_courses[0],
            },
            {
                "title": "Переменные и типы данных",
                "description": "Переменные. Как их поменять, присвоить, отжать",
                "course": created_courses[0],
            },
            {
                "title": "Основы Django",
                "description": "Познакомишься с Django и точно чекушка треснет",
                "course": created_courses[1],
            },
            {
                "title": "Модели в Django",
                "description": "Это не те модели, у которых ноги от ушей, не обламывайтесь",
                "course": created_courses[1],
            },
            {
                "title": "Синтаксис JavaScript",
                "description": "Точечки, запятушки, скобочки... Жуть!!!",
                "course": created_courses[2],
            },
        ]

        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                title=lesson_data["title"], course=lesson_data["course"], defaults=lesson_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан урок: {lesson.title} (курс: {lesson.course.title})"))
            else:
                self.stdout.write(self.style.WARNING(f"Урок уже существует: {lesson.title}"))
