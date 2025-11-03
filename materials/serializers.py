from rest_framework import serializers

from materials.models import Course, Lesson, Subscription
from materials.validators import YouTubeURLValidator
from users.models import Payment


class LessonSerializer(serializers.ModelSerializer):
    # Добавляем валидатор в поле сериализатора
    video_url = serializers.URLField(
        required=False, allow_null=True, allow_blank=True, validators=[YouTubeURLValidator()]
    )

    class Meta:
        model = Lesson
        fields = "__all__"

    def validate(self, data):
        """
        Дополнительная валидация для проверки ссылок
        """
        # Проверяем поле video_url, если оно присутствует в данных
        video_url = data.get("video_url")
        if video_url:
            validator = YouTubeURLValidator()
            try:
                validator(video_url)
            except Exception as e:
                raise serializers.ValidationError({"video_url": str(e)})

        return data


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source="lessons_set")
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "preview", "description", "lessons", "lessons_count", "owner", "is_subscribed"]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки"""

    course_title = serializers.CharField(source="course.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "subscribed_at", "course_title", "user_email"]
        read_only_fields = ["user", "subscribed_at"]


class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "course",
            "course_title",
            "user_email",
            "stripe_session_id",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]


class CreatePaymentSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    success_url = serializers.URLField(default="http://localhost:8000/success/")
    cancel_url = serializers.URLField(default="http://localhost:8000/cancel/")
