# Author: Roberto Piazza
# Date: 05.01.2023

from rest_framework import serializers
from rest_framework.authtoken.models import Token
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


class PortfolioTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioType
        fields = '__all__'


class AssetOwnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetOwned
        fields = '__all__'


class AssetInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetInfo
        fields = '__all__'


class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Setzt den aktuellen User automatisch

    class Meta:
        model = Transaction
        fields = '__all__'
        extra_kwargs = {
            'asset': {'write_only': True},
            'tx_type': {'write_only': True},
            'user': {'read_only': True},
        }

    def validate_asset(self, value):
        # Konvertieren Sie den Asset-Namen in ein Asset-Objekt
        try:
            token = self.context['request'].auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            asset = AssetOwned.objects.get(api_id_name=value, user=user)
            return asset
        except AssetOwned.DoesNotExist:
            raise serializers.ValidationError("Das angegebene Asset existiert nicht.")

    def validate_tx_type(self, value):
        # Konvertieren Sie den Transaktionstyp in ein TransactionType-Objekt
        try:
            tx_type = TransactionType.objects.get(type=value)
            return tx_type
        except TransactionType.DoesNotExist:
            raise serializers.ValidationError("Der angegebene Transaktionstyp ist ungültig.")

    # Ergänzen Sie die Validierung für tx_amount, tx_value und tx_date entsprechend

    # def validate(self, data):
    #     # Überprüfen der erforderlichen Felder
    #     print(data)
    #     required_fields = ['transactionType', 'transactionDate', 'asset', 'amount', 'price']
    #     for field in required_fields:
    #         if not data.get(field):
    #             raise serializers.ValidationError({field: f"Das Feld {field} ist erforderlich."})
    #
    #     # Überprüfen, ob amount, price und transactionFee numerisch sind
    #     numeric_fields = ['amount', 'price', 'transactionFee']
    #     for field in numeric_fields:
    #         try:
    #             # Konvertieren in float, falls das Feld nicht leer und eine Zeichenkette ist
    #             if isinstance(data.get(field, None), str):
    #                 data[field] = float(data[field].replace(',', '.'))
    #         except ValueError:
    #             raise serializers.ValidationError({field: f"Das Feld {field} muss eine Zahl sein."})
    #
    #     # Überprüfen, ob transactionDate ein gültiges Datum ist
    #     if 'transactionDate' in data:
    #         # Hier könnte man eine spezifischere Validierung hinzufügen
    #         pass
    #
    #     # Überprüfen, ob transactionType gültig ist
    #     if 'transactionType' in data:
    #         if not TransactionType.objects.filter(id=data['transactionType']).exists():
    #             raise serializers.ValidationError({'transactionType': "Ungültiger Transaktionstyp."})
    #
    #     # Weitere Validierungen können hier hinzugefügt werden
    #
    #     return data

    # def create(self, validated_data):
        # Logik zum Erstellen einer neuen Transaktion
        # print(validated_data)
        # transaction = Transaction.objects.create(**validated_data)
        # return transaction

