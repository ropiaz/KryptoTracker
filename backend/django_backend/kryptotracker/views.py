from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
# dependencies rest_framework
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# dependencies serializers
from .serializers import UserLoginSerializer, UserSerializer


class LoginAPIView(APIView):
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
                login(request, user)

                token, created = Token.objects.get_or_create(user=user)
                if not created:
                    token.delete()
                    token = Token.objects.create(user=user)

                return Response(data={'detail': user_serializer.data, 'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response(data={'detail': 'Falsches Passwort.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
