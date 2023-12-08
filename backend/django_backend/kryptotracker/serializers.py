# Author: Roberto Piazza
# Date: 18.11.2023
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

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
        if not User.objects.filter(email=email).exists():
            detail = ["E-Mail nicht gefunden."]
            raise serializers.ValidationError(detail=detail)
        return email

class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password"]

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            detail = "Username bereits vergeben!"
            raise serializers.ValidationError(detail=detail)
        return username

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            detail = "E-Mail bereits vergeben!"
            raise serializers.ValidationError(detail=detail)
        return email

    def validate_password(self, password):
        if len(password) < 6:
            detail = "Passwort muss mind. 6 Zeichen lang sein."
            raise serializers.ValidationError(detail=detail)

        # TODO: define more rules for password

        return make_password(password)

class UserEditSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password"]
