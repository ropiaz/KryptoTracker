# Author: Roberto Piazza
# Date: 03.01.2023

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import *


class UserSerializer(serializers.ModelSerializer):
    """Return User JSON Object. PW excluded."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'date_joined']
        extra_kwargs = {'password': {'write_only': True}}


class UserLoginSerializer(serializers.ModelSerializer):
    """Validate Email and return User JSON Object only with email and pw."""
    class Meta:
        model = User
        fields = ['email', 'password']

    def validate_email(self, email):
        """Check if the e-mail exists"""
        if not User.objects.filter(email=email).exists():
            detail = ["E-Mail nicht gefunden."]
            raise serializers.ValidationError(detail=detail)
        return email


class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password"]

    def validate_username(self, username):
        """Check if the username already exists"""
        if User.objects.filter(username=username).exists():
            detail = "Username bereits vergeben!"
            raise serializers.ValidationError(detail=detail)
        return username

    def validate_email(self, email):
        """Check if the e-mail already exists"""
        if User.objects.filter(email=email).exists():
            detail = "E-Mail bereits vergeben!"
            raise serializers.ValidationError(detail=detail)
        return email

    def validate_password(self, password):
        """Check if the password length >= 6"""
        if len(password) < 6:
            detail = "Passwort muss mind. 6 Zeichen lang sein."
            raise serializers.ValidationError(detail=detail)

        # TODO: define more rules for password

        return make_password(password)


class UserEditSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=True)
    passwordConfirmed = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "password", "passwordConfirmed", "date_joined"]

    def validate(self, data):
        """Check whether the password matches with confirmed password and password length >= 6"""
        if 'password' in data and 'passwordConfirmed' in data:
            if data['password'] != data['passwordConfirmed']:
                detail = "Die Passwörter stimmen nicht überein."
                raise serializers.ValidationError(detail=detail)
            if len(data['password']) < 6:
                detail = "Passwort muss mind. 6 Zeichen lang sein."
                raise serializers.ValidationError(detail=detail)
        return data

    def validate_email(self, value):
        """Check whether the e-mail already exists and does not belong to the current user"""
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            detail = "Diese E-Mail-Adresse wird bereits verwendet."
            raise serializers.ValidationError(detail=detail)
        return value

    def validate_username(self, value):
        """Check whether the username already exists and does not belong to the current user"""
        if User.objects.filter(username=value).exclude(id=self.instance.id).exists():
            detail = "Dieser Benutzername wird bereits verwendet."
            raise serializers.ValidationError(detail=detail)
        return value

    def update(self, instance, validated_data):
        """Update user with validated data and hash password"""
        validated_data.pop('passwordConfirmed', None)

        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'


class AssetOwnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetOwned
        fields = '__all__'


class AssetInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetInfo
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
