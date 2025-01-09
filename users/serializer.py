from rest_framework import serializers
from .models import User
from .models import UserProfileType


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'name', 'profile_type', 'phone_number', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  
        user.clean()
        user.save()  
        return user    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'profile_type']  
