from rest_framework import serializers
from .models import User
from .models import UserProfileType

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = '__all__'

    def create(self, validated_data):
            user = User(
                email=validated_data['email'], 
                name=validated_data.get('name', ''), 
                phone_number=validated_data.get('phone_number', ''),
                profile_type=validated_data.get('profile_type', UserProfileType.PARTICIPANT)
            )
            user.set_password(validated_data['password'])  
            user.save()  
            return user    
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= ['email', 'name', 'profile_type']

