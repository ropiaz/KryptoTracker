# Author: Roberto Piazza
# Date: 03.01.2023

# models import and django auth functions
from django.db.models import Q
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# dependencies rest_framework
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# dependencies serializers
from .serializers import *
# python and other dependencies
from datetime import datetime


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
                logout(request)
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
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                if not created:
                    token.delete()
                    token = Token.objects.create(user=user)

                return Response(data={'token': token.key}, status=status.HTTP_200_OK)
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
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response(data={'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response(data={'detail': 'Registrierung fehlgeschlagen. Bitte erneut versuchen.'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthUser(APIView):
    """Handle User Auth with Token. Check if user is authenticated and token is in database. Return user data with
    status code. Otherwise return error messages."""

    def get(self, request):
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


class EditUser(APIView):
    """Handle User Edit with Token. Check if user is authenticated and token is in database. Validate new user data and
        Return user with updated data with and status code. Otherwise return error messages."""
    authentication_classes = [TokenAuthentication]

    def put(self, request, token):
        try:
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                user_serializer = UserEditSerializer(user, data=request.data)
                if user_serializer.is_valid():
                    user_serializer.save()
                    return Response(status=status.HTTP_200_OK)
                return Response(data=user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Token.DoesNotExist:
            return Response({'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)


class DashboardAPIView(APIView):
    """API View for handling and displaying dashboard values."""
    authentication_classes = [TokenAuthentication]

    def get_balances(self, portfolios):
        """Calculate sum balance of all portfolios and extract each balance from one portfolio"""
        sum_balance = 0.0
        spot_balance = 0.0
        staking_balance = 0.0
        for data in portfolios:
            sum_balance += float(data['balance'])
            if data['portfolio_type'] == 1:
                staking_balance = float(data['balance'])
            if data['portfolio_type'] == 2:
                spot_balance = float(data['balance'])

        return sum_balance, spot_balance, staking_balance


    # TODO: calculate trend for each asset
    def get_assets_in_portfolios(self, user):
        """Returns two lists containing the assets from staking and spot portfolio"""
        # get all asset infos from database
        asset_infos = AssetInfo.objects.all()
        asset_infos_serializer = AssetInfoSerializer(asset_infos, many=True)

        spot = []
        asset_owned_in_spot = AssetOwned.objects.filter(portfolio__portfolio_type=1, portfolio__user=user, asset__in=asset_infos)
        for owned in asset_owned_in_spot:
            currency = {
                'acronym': owned.asset.acronym.upper(),
                'img': owned.asset.image,
                'amount': owned.quantity_owned,
                'price': owned.asset.current_price,
                'owned_value': owned.quantity_price,
                'trend': '1,00%'
            }
            spot.append(currency)

        staking = []
        asset_owned_in_staking = AssetOwned.objects.filter(portfolio__portfolio_type=2, portfolio__user=user, asset__in=asset_infos)
        for owned in asset_owned_in_staking:
            currency = {
                'acronym': owned.asset.acronym.upper(),
                'img': owned.asset.image,
                'amount': owned.quantity_owned,
                'price': owned.asset.current_price,
                'owned_value': owned.quantity_price,
                'trend': '0,00%'
            }
            staking.append(currency)
        return spot, staking


    def get_transactions_data(self, user):
        """Get all transactions and extract necessary data"""
        transactions = Transaction.objects.filter(
            Q(user=user) |
            Q(asset__portfolio__user=user)
        ).order_by('tx_date')
        transactions_serializer = TransactionSerializer(transactions, many=True)
        count_transactions = len(transactions_serializer.data)

        # TODO BUGFIX: extract first and last transaction
        first_transaction = transactions.first()
        first_transaction_formatted = first_transaction.tx_date.strftime(
            '%d.%m.%Y %H:%M') if first_transaction else "Keine Daten verfügbar"
        last_transaction = transactions.last()
        last_transaction_formatted = last_transaction.tx_date.strftime(
            '%d.%m.%Y %H:%M') if last_transaction else "Keine Daten verfügbar"

        # get last five transactions
        last_five_transactions = Transaction.objects.filter(
            Q(user=user) |
            Q(asset__portfolio__user=user)
        ).order_by('-tx_date')[:5]
        last_five_transactions_serializer = TransactionSerializer(last_five_transactions, many=True)

        transaction_assets = []

        for tx in last_five_transactions_serializer.data:
            asset_owned = AssetOwned.objects.get(id=tx['asset'])
            tx_date_obj = datetime.fromisoformat(tx['tx_date'])
            tx_date_formatted = tx_date_obj.strftime('%d.%m.%Y %H:%M')

            transaction_assets.append(
                {
                    'tx_date': tx_date_formatted,
                    'tx_amount': tx['tx_amount'],
                    'tx_value': tx['tx_value'],
                    'tx_type': tx['tx_type'],
                    'asset': asset_owned.asset.acronym.upper()
                }
            )
        return count_transactions, first_transaction_formatted, last_transaction_formatted, transaction_assets

    def get(self, request):
        """GET Route /api/dashboard for dashboard"""
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                # get balances from portfolios
                portfolios = Portfolio.objects.filter(user=user)
                portfolio_serializer = PortfolioSerializer(portfolios, many=True)
                sum_balance, spot_balance, staking_balance = self.get_balances(portfolio_serializer.data)

                # get owned assets
                asset_owned = AssetOwned.objects.filter(portfolio__in=portfolios)
                asset_owned_serializer = AssetOwnedSerializer(asset_owned, many=True)
                count_asset_owned = len(asset_owned_serializer.data)

                # get all transactions and extract necessary data
                count_transactions, first_transaction_formatted, last_transaction_formatted, last_five_transactions = self.get_transactions_data(user=user)

                # get the user related balances (assets in spot and staking)
                spot, staking = self.get_assets_in_portfolios(user)

                context = {
                    # variables for stat cards
                    'sum_balance': sum_balance,
                    'spot_balance': spot_balance,
                    'staking_balance': staking_balance,
                    'first_transaction': first_transaction_formatted,
                    'last_transaction': last_transaction_formatted,
                    'transactions': {'count': count_transactions, 'with_coins': count_asset_owned},
                    # variables for balance tables
                    'spot_data': spot,
                    'staking_data': staking,
                    # variable for last transactions list
                    'last_five_transactions': last_five_transactions,
                }
                return Response(data=context, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)
