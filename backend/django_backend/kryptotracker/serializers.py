from rest_framework import serializers
from django.contrib.auth.models import User

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
