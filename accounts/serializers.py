from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=('email','password','role')

    def create(self,validated_data):
        user=User(
            email=validated_data['email'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

from .models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model=Job
        fields='__all__'
        read_only_fields=('recruiter','created_at','status')
