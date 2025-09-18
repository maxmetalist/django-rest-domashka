from django.db.models import Count
from rest_framework import viewsets, generics
from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """Контроллер курсов через ViewSet"""
    queryset = Course.objects.annotate(lessons_count=Count('lessons'))
    serializer_class = CourseSerializer


# Контроллеры уроков через generic
class LessonListAPIView(generics.ListAPIView):
    """Списка уроков"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Одного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonCreateAPIView(generics.CreateAPIView):
    """Для создания урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonUpdateAPIView(generics.UpdateAPIView):
    """Для обновления урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonDestroyAPIView(generics.DestroyAPIView):
    """Для удаления урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
