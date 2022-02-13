from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


class MyUserSerializer(serializers.ModelSerializer):

    def validate_password(self, value: str) -> str:
        """
        Hash value passed by user.

        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)

    class Meta:
        model = User
        fields = ('email', 'password', 'firstname', 'lastname')

        # These fields are displayed but not editable and have to be a part of 'fields' tuple
        read_only_fields = ('is_active', 'is_staff', 'is_superuser',)

        # These fields are only editable (not displayed) and have to be a part of 'fields' tuple
        extra_kwargs = {'password': {'write_only': True, 'min_length': 4}}



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        # Add custom claims
        user.set_active()
        token['username'] = user.email

        return token


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenRefreshSerializer, cls).refresh(user)
        # Add custom claims
        # token['username'] = user.email
        return token
