from rest_framework import serializers
from .models import User
from phonenumber_field.serializerfields import PhoneNumberField


class UserSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar')
        read_only_fields = ('email',)  # email нельзя менять через этот эндпоинт
