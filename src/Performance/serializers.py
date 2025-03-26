from rest_framework import serializers
from .models import CustomerUser


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['email', 'username', 'first_name', 'last_name', 'gender', 'country', 'phone_number', 'image', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomerUser(
            email=validated_data['email'],
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            gender=validated_data.get('gender'),
            country=validated_data.get('country'),
            phone_number=validated_data.get('phone_number'),
            image=validated_data.get('image'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


