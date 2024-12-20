from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = '__all__'
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= ['email', 'name', 'profile_type']

