from rest_framework import serializers

from materials.models import Course, Lesson
from users.models import User, Payment
from phonenumber_field.serializerfields import PhoneNumberField


class UserSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar')
        read_only_fields = ('email',)  # email нельзя менять через этот эндпоинт


class CourseShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title']


class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title']


class PaymentSerializer(serializers.ModelSerializer):
    paid_course_detail = CourseShortSerializer(source='paid_course', read_only=True)
    paid_lesson_detail = LessonShortSerializer(source='paid_lesson', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_date', 'paid_course', 'paid_lesson',
            'paid_course_detail', 'paid_lesson_detail', 'amount',
            'payment_method', 'payment_method_display'
        ]
        read_only_fields = ['user', 'payment_date']


class UserProfileSerializer(serializers.ModelSerializer):
    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'city', 'avatar',
            'first_name', 'last_name', 'payment_history'
        ]
        read_only_fields = ['id', 'email']

    def get_payment_history(self, obj):
        # Получаем платежи пользователя, отсортированные по дате
        payments = Payment.objects.filter(user=obj).order_by('-payment_date')
        return PaymentSerializer(payments, many=True).data
