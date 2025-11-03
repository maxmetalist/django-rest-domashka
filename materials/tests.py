# Хренова туча тестов дя уроков и подписок
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    """Тестирование CRUD операций для уроков"""

    def setUp(self):
        """Настройка тестовых данных"""
        # Создаём юзеров
        self.regular_user = User.objects.create_user(email="test@example.com", password="testpass123")

        self.another_user = User.objects.create_user(email="another@example.com", password="testpass123")

        # Создаём модератора
        self.moderator = User.objects.create_user(email="moderator@example.com", password="testpass123")

        # Создаём курсы
        self.course = Course.objects.create(
            title="Test Course", description="Test Description", owner=self.regular_user, price=1000.00
        )

        # Создаём уроки
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Description",
            course=self.course,
            video_url="https://www.youtube.com/watch?v=test",
            owner=self.regular_user,
        )

        self.client.force_authenticate(user=self.regular_user)

        # Создаём группу модераторов
        self.moderators_group, created = Group.objects.get_or_create(name="moderators")
        self.moderator.groups.add(self.moderators_group)

        # Urls для тестов
        self.lessons_list_url = reverse("lesson-list")  # Список уроков
        self.lesson_detail_url = reverse("lesson-detail", kwargs={"pk": self.lesson.pk})  # Детали урока

    def test_get_lessons_list_regular_user(self):
        """Тест получения списка уроков обычным пользователем"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=newlesson",
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_lessons_list_moderator(self):
        """Тест получения списка уроков модератором"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_lesson_detail_owner(self):
        """Тест получения деталей урока владельцем"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Lesson")

    def test_get_lesson_detail_moderator(self):
        """Тест получения деталей урока модератором"""
        self.moderator.groups.add(self.moderators_group)

        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_lesson_detail_unauthorized(self):
        """Тест получения деталей урока неавторизованным пользователем"""
        self.client.force_authenticate(user=None)
        url = reverse("lesson-detail", args=[self.lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_lesson_detail_another_user(self):
        """Тест получения деталей урока другим пользователем"""
        self.client.force_authenticate(user=self.another_user)
        response = self.client.get(self.lesson_detail_url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_create_lesson_regular_user(self):
        """Тест создания урока обычным пользователем"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=newlesson",
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_moderator_forbidden(self):
        """Тест создания урока модератором"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "Урок от модератора",
            "description": "Описание урока",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/watch?v=moderatorlesson",
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_invalid_url(self):
        """Тест создания урока с невалидной ссылкой"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "title": "Урок с невалидной ссылкой",
            "description": "Описание урока",
            "course": self.course.id,
            "video_url": "https://vk.com/video123",
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        url = reverse("lesson-detail", args=[self.lesson.id])
        update_data = {
            "title": "Updated Lesson Title",
            "description": "Updated Description",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "course": self.course.id,
        }

        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated Lesson Title")

    def test_update_lesson_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "Урок обновлен модератором"}
        response = self.client.patch(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_another_user(self):
        """Тест обновления урока другим пользователем"""
        self.client.force_authenticate(user=self.another_user)
        data = {"title": "Попытка чужого обновления"}
        response = self.client.patch(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_moderator_forbidden(self):
        """Тест удаления урока модератором"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_another_user(self):
        """Тест удаления урока другим пользователем"""
        self.client.force_authenticate(user=self.another_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class SubscriptionTestCase(APITestCase):
    """Тестирование функционала подписок"""

    def setUp(self):
        """Настройка тестовых данных"""

        # Создаем пользователей
        self.user1 = User.objects.create_user(email="user1@test.com", password="testpass123")

        self.user2 = User.objects.create_user(email="user2@test.com", password="testpass123")

        # Создаем курсы
        self.course1 = Course.objects.create(
            title="Курс 1", description="Описание курса 1", owner=self.user1, price=2000.00
        )

        self.course2 = Course.objects.create(
            title="Курс 2", description="Описание курса 2", owner=self.user2, price=1000.00
        )

        self.client.force_authenticate(user=self.user1)

        # Создаём группу модераторов
        self.moderators_group, created = Group.objects.get_or_create(name="moderators")

        # URL для тестирования
        self.subscriptions_url = reverse("subscriptions")  # Список и создание подписок
        self.subscription_detail_url = lambda pk: reverse("subscription-detail", kwargs={"pk": pk})

    def test_create_subscription(self):
        """Тест создания подписки"""
        self.client.force_authenticate(user=self.user1)
        data = {"course_id": self.course1.id}
        response = self.client.post(self.subscriptions_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("У тя подписка на курс", response.data["message"])

    def test_create_subscription_duplicate(self):
        """Тест создания дублирующей подписки (должна отписывать)"""
        url = reverse("subscriptions")

        data = {"course_id": self.course1.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_subscription_unauthorized(self):
        """Тест создания подписки неавторизованным пользователем"""
        self.client.force_authenticate(user=None)

        url = reverse("subscriptions")
        data = {"course_id": self.course1.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_subscription_invalid_course(self):
        """Тест создания подписки на несуществующий курс"""
        self.client.force_authenticate(user=self.user1)

        data = {"course_id": 999}  # Несуществующий ID

        response = self.client.post(self.subscriptions_url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_subscription_missing_course_id(self):
        """Тест создания подписки без course_id"""
        self.client.force_authenticate(user=self.user1)

        data = {}  # Отсутствует course_id

        response = self.client.post(self.subscriptions_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course_id", response.data["error"])

    def test_get_subscriptions_list(self):
        """Тест получения списка подписок пользователя"""
        Subscription.objects.create(user=self.user1, course=self.course1)
        Subscription.objects.create(user=self.user1, course=self.course2)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.subscriptions_url)
        self.assertEqual(len(response.data), 2)

    def test_delete_subscription_owner(self):
        """Тест удаления подписки владельцем"""
        subscription = Subscription.objects.create(user=self.user1, course=self.course1)

        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(self.subscription_detail_url(subscription.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.count(), 0)
        self.assertIn("Вы отписались от курса", response.data["message"])

    def test_delete_subscription_another_user(self):
        """Тест удаления чужой подписки"""
        subscription = Subscription.objects.create(user=self.user1, course=self.course1)

        self.client.force_authenticate(user=self.user2)  # Другой пользователь

        response = self.client.delete(self.subscription_detail_url(subscription.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Subscription.objects.count(), 1)  # Подписка осталась

    def test_delete_nonexistent_subscription(self):
        """Тест удаления несуществующей подписки"""
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(self.subscription_detail_url(999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_serializer_with_subscription(self):
        """Тест сериализатора курса с информацией о подписке"""
        Subscription.objects.create(user=self.user1, course=self.course1)

        self.client.force_authenticate(user=self.user1)
        course_detail_url = reverse("course-detail", kwargs={"pk": self.course1.id})
        response = self.client.get(course_detail_url)

        self.assertIn("is_subscribed", response.data)
        self.assertTrue(response.data["is_subscribed"])


class PaginationTestCase(APITestCase):
    """Тестирование пагинации"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(email="test@test.com", password="testpass123")

        self.course = Course.objects.create(
            title="Тестовый курс", description="Описание", owner=self.user, price=1500.00
        )

        # Создаем несколько уроков для тестирования пагинации
        for i in range(15):
            Lesson.objects.create(
                title=f"Урок {i + 1}",
                description=f"Описание урока {i + 1}",
                course=self.course,
                owner=self.user,
                video_url=f"https://www.youtube.com/watch?v=test{i + 1}",
            )

        self.lessons_url = reverse("lesson-list")

    def test_pagination_default(self):
        """Тест пагинации по умолчанию"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.lessons_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)  # page_size по умолчанию
        self.assertEqual(response.data["count"], 15)  # Всего уроков

    def test_pagination_custom_page_size(self):
        """Тест пагинации с кастомным размером страницы"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.lessons_url, {"page_size": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])  # Должна быть следующая страница

    def test_pagination_max_page_size(self):
        """Тест ограничения максимального размера страницы"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.lessons_url, {"page_size": 100})  # Больше max_page_size

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]), 50)  # Не больше max_page_size
