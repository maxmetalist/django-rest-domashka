from django.db.models import Count
from rest_framework import viewsets, generics, permissions
from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from materials.permissions import IsOwnerOrModerator, IsNotModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """Контроллер курсов через ViewSet"""
    queryset = Course.objects.annotate(lessons_count=Count('lessons'))
    serializer_class = CourseSerializer

    def get_permissions(self):
        """Динамическое назначение прав в зависимости от действия"""
        if self.action == 'create':
            # Создавать могут только не-модераторы
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action == 'destroy':
            # Удалять могут только не-модераторы и только свои курсы
            return [permissions.IsAuthenticated(), IsNotModerator(), IsOwner()]
        elif self.action in ['update', 'partial_update']:
            # Редактировать могут владельцы или модераторы
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        else:
            # Просматривать могут все аутентифицированные (аноним в обломе)
            return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Автоматически назначаем владельца при создании"""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Фильтрация queryset в зависимости от прав"""
        user = self.request.user

        # Модераторы видят все курсы (но только для чтения)
        if user.groups.filter(name='moderators').exists():
            return Course.objects.annotate(lessons_count=Count('lessons'))

        # Анонимные юзеры не видят ничего
        if not user.is_authenticated:
            return Course.objects.none()

        # Обычные юзеры видят только свои курсы
        return Course.objects.filter(owner=user).annotate(lessons_count=Count('lessons'))


# Контроллеры уроков через generic
class LessonListAPIView(generics.ListAPIView):
    """Списка уроков"""
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Модераторы видят все уроки (но только для чтения)
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        # Обычные юзеры видят только свои уроки
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Одного урока"""
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]

    def get_queryset(self):
        user = self.request.user

        # Модераторы видят все уроки
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        # Обычные юзеры видят только свои уроки
        return Lesson.objects.filter(owner=user)


class LessonCreateAPIView(generics.CreateAPIView):
    """Для создания урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Для обновления урока"""
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user

        # Обычные юзеры могут редактировать только свои уроки(permission IsOwner проверит владельца)
        return Lesson.objects.all()


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Для удаления урока"""
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotModerator, IsOwner]

    def get_queryset(self):
        user = self.request.user

        # Обычные юзеры могут удалять только свои уроки (permisson'ы проверят владельца)
        return Lesson.objects.filter(owner=user)
