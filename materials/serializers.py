from rest_framework import serializers
from materials.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source="lessons_set")

    class Meta:
        model = Course
        fields = [
            "id", "title", "preview", "description", "lessons", "lessons_count"
        ]

    def get_lessons_count(self, obj):
        if hasattr(obj, 'lessons_count'):
            return obj.lessons_count
        return obj.lessons.count()
