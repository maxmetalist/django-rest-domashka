import django_filters
from users.models import Payment
from materials.models import Course, Lesson


class PaymentFilter(django_filters.FilterSet):
    paid_course = django_filters.ModelChoiceFilter(
        field_name="paid_course", queryset=Course.objects.all(), label="Курс"
    )
    paid_lesson = django_filters.ModelChoiceFilter(
        field_name="paid_lesson", queryset=Lesson.objects.all(), label="Урок"
    )
    payment_method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHOD_CHOICES, label="Способ оплаты")
    ordering = django_filters.OrderingFilter(
        fields=(("payment_date", "payment_date"),),
        field_labels={
            "payment_date": "Дата оплаты",
        },
        label="Сортировка",
    )

    class Meta:
        model = Payment
        fields = ["paid_course", "paid_lesson", "payment_method"]
