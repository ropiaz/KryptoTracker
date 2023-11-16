from django.contrib.auth.models import User
from django.contrib.auth import authenticate
# dependencies rest_framework
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
# dependencies serializers
from .serializers import UserLoginSerializer, UserSerializer, UserRegisterSerializer
from rest_framework.serializers import ValidationError


class LogoutAPI(APIView):
    """Handle User Logout. Check if user is authenticated and token is in database. Delete token and return success
    message with status code. Otherwise return error messages."""
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kargs):
        token = request.auth
        if token is not None:
            try:
                token_obj = Token.objects.get(key=token)
                # user = token_obj.user
                token_obj.delete()

                return Response({'detail': 'Logout erfolgreich.'}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response({'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Kein Token vorhanden.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    """Handle User Login. Check if user is in database and check credentials.
    Return User data with Token. Otherwise return error messages."""

    def post(self, request, *args, **kargs):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')

            try:
                username = User.objects.get(email=email).username
            except:
                username = None

            user = authenticate(username=username, password=password)

            if user is not None:
                user_serializer = UserSerializer(user)

                token, created = Token.objects.get_or_create(user=user)
                if not created:
                    token.delete()
                    token = Token.objects.create(user=user)

                return Response(data={'detail': user_serializer.data, 'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response(data={'detail': 'Falsches Passwort.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterAPI(APIView):
    """Handle User Registration. Check if username and email is unique and validate credentials.
        Return User data with Token. Otherwise return error messages."""
    def post(self, request, *args, **kargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=serializer.validated_data['username'])
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                user_serializer = UserSerializer(user)
                return Response(data={'detail': user_serializer.data, 'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response(data={'detail': 'Registrierung fehlgeschlagen. Bitte erneut versuchen.'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # raise ValidationError(
        #     serializer.errors, code=status.HTTP_406_NOT_ACCEPTABLE)


class AuthUser(APIView):
    """Handle User Auth with Token. Check if user is authenticated and token is in database. Return user data with
    status code. Otherwise return error messages."""

    def get(self, request, *args, **kargs):
        token = request.auth
        if token is not None:
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                if user is not None:
                    user_serializer = UserSerializer(user)
                    return Response(data={'detail': user_serializer.data}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response({'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Kein Token vorhanden.'}, status=status.HTTP_400_BAD_REQUEST)