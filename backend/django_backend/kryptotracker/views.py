# Author: Roberto Piazza
# Date: 21.01.2023

# models import and django auth functions
from django.db.models import Q
from .models import PortfolioType, Portfolio, AssetInfo, AssetOwned, Comment, TransactionType, Transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
# dependencies rest_framework
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# dependencies serializers
from .serializers import *
# python and other dependencies
from .utils.crypto_data import get_currency_data, get_historical_price_at_time, convert_crypto_amount, get_crypto_data_from_coinmarketcap, get_historical_price_at_time_coingecko
from datetime import datetime, timedelta
import pandas as pd
import pytz


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

    # TODO: update prices from owned assets every 30 min?
    def update_currency_prices(self):
        pass

    def get_balances(self, portfolios):
        """Calculate sum balance of all portfolios and extract each balance from one portfolio"""
        sum_balance = 0.0
        spot_balance = 0.0
        staking_balance = 0.0
        for data in portfolios:
            sum_balance += float(data['balance'])
            if PortfolioType.objects.get(id=data['portfolio_type']).type == 'Spot':
                spot_balance += float(data['balance'])
            if PortfolioType.objects.get(id=data['portfolio_type']).type == 'Staking':
                staking_balance += float(data['balance'])
        return sum_balance, spot_balance, staking_balance

    # TODO: calculate trend for each asset
    def get_assets_in_portfolios(self, user, asset_infos):
        """Returns lists containing the assets from all staking and spot portfolios"""
        # get all owned Assets to a user
        owned = AssetOwned.objects.filter(
            portfolio__user=user,
            asset__in=asset_infos
        )

        # combine owned assets and portfolio to display each portfolio and their assets
        data = []
        for portfolio in Portfolio.objects.filter(user=user):
            currencies = []
            for own in owned:
                if own.portfolio == portfolio:
                    currency = {
                        'acronym': own.asset.acronym.upper(),
                        'img': own.asset.image,
                        'amount': own.quantity_owned,
                        'price': own.asset.current_price,
                        'owned_value': own.quantity_price,
                        'trend': '1.00%'
                    }
                    currencies.append(currency)

            # sort currencies in ascending order based on the acronyms
            currencies.sort(key=lambda currency: currency['acronym'])

            portfolio_data = {
                'name': portfolio.name,
                'type': portfolio.portfolio_type.type,
                'currencies': currencies
            }
            data.append(portfolio_data)

        data.sort(key=lambda portfolio: portfolio['name'])
        return data

    def get_transactions_data(self, user):
        """Get all transactions and extract necessary data"""
        transactions = Transaction.objects.filter(
            Q(user=user) |
            Q(asset__portfolio__user=user)
        ).order_by('tx_date')
        transactions_serializer = TransactionSerializer(transactions, many=True)
        count_transactions = len(transactions_serializer.data)

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
            tx_date_obj_utc = tx_date_obj.astimezone(pytz.UTC)
            tx_date_formatted = tx_date_obj_utc.strftime('%d.%m.%Y %H:%M')
            tx_type = TransactionType.objects.get(id=tx['tx_type']).type

            transaction_assets.append(
                {
                    'tx_date': tx_date_formatted,
                    'tx_amount': tx['tx_amount'],
                    'tx_value': tx['tx_value'],
                    'tx_type': tx_type,
                    'asset': asset_owned.asset.acronym.upper()
                }
            )
        return count_transactions, first_transaction_formatted, last_transaction_formatted, transaction_assets

    # TODO: represent duplicate assets as one
    def get_chart_data(self, user, asset_infos):
        """Return all owned assets with acronym and their value in euro."""
        # get all owned assets from all portfolios that belongs to a user
        asset_owned = AssetOwned.objects.filter(portfolio__user=user, asset__in=asset_infos)
        data = []
        for owned in asset_owned:
            data.append({
                'asset': owned.asset.acronym.upper(),
                'EUR': round(owned.quantity_price, 3)
            })

        # sort list ASC
        sorted_data = sorted(data, key=lambda x: x['EUR'], reverse=True)

        return sorted_data

    def get_tax_data(self):
        """TODO: get and return tax data for dashboard """
        pass

    # TODO: get and return Tax data
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

                # get all asset infos from database
                asset_infos = AssetInfo.objects.all()

                # get the user related balances (assets in spot and staking)
                all_portfolios_data = self.get_assets_in_portfolios(user, asset_infos)

                # get chart data
                chart_data = self.get_chart_data(user, asset_infos)
                context = {
                    # variables for stat cards
                    'sum_balance': sum_balance,
                    'spot_balance': spot_balance,
                    'staking_balance': staking_balance,
                    'first_transaction': first_transaction_formatted,
                    'last_transaction': last_transaction_formatted,
                    'transactions': {'count': count_transactions, 'with_coins': count_asset_owned},
                    # variables for balance tables
                    'portfolios_data': all_portfolios_data,
                    # variable for last transactions list
                    'last_five_transactions': last_five_transactions,
                    # variable for bar chart
                    'chart_data': chart_data,
                    # variable for tax_data
                    'tax_data': {'dummy': 'dummy'}
                }
                return Response(data=context, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)


class AssetOwnedAPIView(APIView):
    """API View for handling CRUD operations on AssetOwned model."""
    authentication_classes = [TokenAuthentication]

    # TODO: update asset only if last updated > 30 min?
    def update_asset_info(self, asset_info):
        """Update asset info image and current price. If CoinGecko fails use webscraping and get data from coinmarkecap"""
        if asset_info.api_id_name == 'euro':
            return

        try:
            # get data from coingecko api
            new_data = get_currency_data(api_id_name=asset_info.api_id_name)
            asset_info.current_price = new_data['current_price']
            asset_info.image = new_data['image']
            asset_info.save()
        except:
            # get data from webscraping coinmarketcap
            data = get_crypto_data_from_coinmarketcap(crypto_name=asset_info.api_id_name)
            asset_info.current_price = data['current_price']
            asset_info.image = data['image']
            asset_info.save()

    def post(self, request):
        """POST Route /api/asset-owned/ create new asset owned object."""
        token = request.auth
        token_obj = Token.objects.get(key=token)
        user = token_obj.user
        if user is not None:
            quantity_owned = request.data['quantity_owned']
            quantity_price = request.data['quantity_price']
            portfolio = Portfolio.objects.get(pk=request.data['portfolio_id'])
            asset_acronym = request.data['asset_acronym'].lower()
            asset_name = request.data['asset_name'].lower()
            asset_info_obj = AssetInfo.objects.filter(acronym=asset_acronym, api_id_name=asset_name).first()

            # find asset in coingecko api and get new data, update AssetInfo object and create new AssetOwned. Update portfolio balance
            if asset_info_obj is not None:
                new_data = get_currency_data(api_id_name=asset_info_obj.api_id_name)

                # update asset infos
                if not quantity_price:
                    self.update_asset_info(asset_info=asset_info_obj)

                asset_owned = AssetOwned.objects.filter(portfolio=portfolio, asset=asset_info_obj).first()
                # TODO: decide when given quantity_price is necessary
                if asset_owned is None:
                    new_owned = AssetOwned.objects.create(
                        quantity_owned=quantity_owned,
                        quantity_price=asset_info_obj.current_price * quantity_owned if not quantity_price else quantity_price,
                        portfolio=portfolio,
                        asset=asset_info_obj
                    )
                    portfolio.balance += new_owned.quantity_price
                    portfolio.save()
                else:
                    # asset already exists in portfolio
                    asset_owned.quantity_owned += quantity_owned
                    asset_owned.save()
                    old_quantity_price = asset_owned.quantity_price
                    asset_owned.quantity_price = new_data['current_price'] * asset_owned.quantity_owned
                    asset_owned.save()
                    portfolio.balance += asset_owned.quantity_price - old_quantity_price
                    portfolio.save()

                return Response(data={"message": "success"}, status=status.HTTP_201_CREATED)
            return Response(data={"error": "Kryptowährung nicht gefunden."}, status=status.HTTP_400_BAD_REQUEST)


class PortfolioTypeAPIView(APIView):
    """API View for handling CRUD operations on PortfolioType model."""
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """GET Route /api/portfolio-type/"""
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                portfolio_types = PortfolioType.objects.all()
                serializer = PortfolioTypeSerializer(portfolio_types, many=True)
                context = {
                    'types': serializer.data
                }
                return Response(data=context, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)


class PortfolioAPIView(APIView):
    """API View for handling CRUD operations on Portfolio model."""
    authentication_classes = [TokenAuthentication]

    def transform_data(self, data):
        """Return only id, name, type"""
        transformed_data = []
        for value in data:
            context = {
                'id': value['id'],
                'name': value['name'],
                'balance': value['balance'],
                'type': PortfolioType.objects.get(id=value['portfolio_type']).type,
            }
            transformed_data.append(context)
        return transformed_data

    def get(self, request):
        """GET Route /api/portfolio/"""
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                portfolios = Portfolio.objects.filter(user=user)
                serializer = PortfolioSerializer(portfolios, many=True)
                t_data = self.transform_data(serializer.data)
                context = {
                    'portfolios': t_data
                }
                return Response(data=context, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """POST Route /api/portfolio/ create new portfolio."""
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                portfolio_type = PortfolioType.objects.get(pk=request.data['portfolio_type_id'])

                if portfolio_type is None:
                    return Response(data={"error": "Portfoliotyp nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

                data = {
                    'name': request.data['name'],
                    'balance': request.data['balance'],
                    'user': user.id,
                    'portfolio_type': portfolio_type.id
                }

                serializer = PortfolioSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(data={"message": "success"}, status=status.HTTP_201_CREATED)
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, pk, format=None):
    #     portfolio = self.get_object(pk)
    #     serializer = PortfolioSerializer(portfolio, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(data=serializer.data, status=status.HTTP_200_OK)
    #     return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     portfolio = self.get_object(pk)
    #     portfolio.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    #
    # def get_object(self, pk):
    #     try:
    #         return Portfolio.objects.get(pk=pk)
    #     except Portfolio.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)


class TransactionTypeAPIView(APIView):
    """API View for handling CRUD operations on TransactionType model."""
    authentication_classes = [TokenAuthentication]

    def get_data_for_create(self, user):
        tx_types = TransactionType.objects.all()
        tx_serializer = TransactionTypeSerializer(tx_types, many=True)

        portfolios = Portfolio.objects.filter(user=user)
        p_serializer = PortfolioSerializer(portfolios, many=True)

        asset_infos = AssetInfo.objects.all().order_by('fullname')
        a_serializer = AssetInfoSerializer(asset_infos, many=True)

        portfolio_data = []
        for portfolio in p_serializer.data:
            context = {
                'id': portfolio['id'],
                'name': portfolio['name'],
                'portfolio_type': PortfolioType.objects.get(id=portfolio['portfolio_type']).type,
            }
            portfolio_data.append(context)
        return tx_serializer.data, portfolio_data, a_serializer.data

    def get(self, request):
        """GET Route /api/transaction-type/"""
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                tx_types, portfolio_data, asset_infos = self.get_data_for_create(user)
                context = {
                    'types': tx_types,
                    'portfolios': portfolio_data,
                    'asset_infos': asset_infos
                }
                return Response(data=context, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)


class TransactionAPIView(APIView):
    """API View for handling CRUD operations on Portfolio model."""
    authentication_classes = [TokenAuthentication]

    def get_transactions_data(self, user):
        """Get and return all user transactions, extract and format necessary data"""
        transactions = Transaction.objects.filter(
            Q(user=user) |
            Q(asset__portfolio__user=user)
        ).order_by('-tx_date')
        transactions_serializer = TransactionSerializer(transactions, many=True)

        txs = []
        for tx in transactions_serializer.data:
            # get data from foreign keys and format date
            asset_owned = AssetOwned.objects.get(id=tx['asset'])
            tx_type = TransactionType.objects.get(id=tx['tx_type'])
            tx_date_obj = datetime.fromisoformat(tx['tx_date'])
            tx_date_obj_utc = tx_date_obj.astimezone(pytz.UTC)
            tx_date_formatted = tx_date_obj_utc.strftime('%d.%m.%Y %H:%M')

            # combine data into dict
            txs.append(
                {
                    'tx_type': tx_type.type,
                    'asset': asset_owned.asset.acronym.upper(),
                    'tx_amount': str(round(tx['tx_amount'], 3)).replace('.', ','),
                    'tx_value': str(round(tx['tx_value'], 3)).replace('.', ','),
                    'tx_fee': str(round(tx['tx_fee'], 3)).replace('.', ','),
                    'tx_date': tx_date_formatted,
                    'tx_sender_address': tx['tx_sender_address'],
                    'tx_recipient_address': tx['tx_recipient_address'],
                    'tx_comment': '' if not tx['tx_comment'] else Comment.objects.get(id=tx['tx_comment']).text,
                }
            )
        return txs

    def get(self, request):
        """GET Route /api/transaction for transactions"""
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                tx_data = self.get_transactions_data(user)
                context = {
                    # variables for transactions list
                    'transactions': tx_data
                }
                return Response(data=context, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)

    # TODO: update asset only if last updated > 30 min? + what if api and scraping fails?
    def update_asset_info(self, asset_info: AssetInfo):
        """Update asset info image and current price. If CoinGecko fails use webscraping and get data from coinmarkecap"""
        if asset_info.api_id_name == 'euro':
            return

        current_time = timezone.now()
        time_delta = timedelta(minutes=30)
        if current_time - asset_info.updated_at < time_delta and asset_info.current_price != 0.0:
            # print(f"{asset_info.fullname} wurde vor weniger als 30 Minuten aktualisiert.")
            return

        try:
            new_data = get_currency_data(api_id_name=asset_info.api_id_name)
            asset_info.current_price = new_data['current_price']
            asset_info.image = new_data['image']
            asset_info.save()
        except:
            data = get_crypto_data_from_coinmarketcap(crypto_name=asset_info.api_id_name)
            asset_info.current_price = data['current_price']
            asset_info.image = data['image']
            asset_info.save()

    # TODO: validate data
    def validate_data(self, user, data):
        portfolio = Portfolio.objects.get(user=user, id=data['portfolio'])
        tx_type = TransactionType.objects.get(id=data['transactionType'])
        tx_date = data['transactionDate']
        tx_asset_name = data['assetName']
        tx_asset_acronym = data['assetAcronym']
        tx_target_asset_name = data['targetAssetName']
        tx_target_asset_acronym = data['targetAssetAcronym']
        tx_amount = data['amount']
        tx_price = data['price']
        tx_fee = data['transactionFee']
        tx_hash_id = data['transactionHashId']
        tx_sender_address = data['senderAddress']
        tx_recipient_address = data['recipientAddress']
        tx_comment = data['comment']

        print(portfolio, tx_type, tx_date, tx_asset_name)

    # TODO: get current currency price if tx_price is given?
    def post(self, request, *args, **kargs):
        """POST Route /api/transaction/ for creating new transactions"""
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                print(request.data)

                # self.validate_data(user, request.data)

                asset_info = AssetInfo.objects.filter(id=request.data['assetId']).first()
                target_asset_info = AssetInfo.objects.filter(id=request.data['targetAssetId']).first()
                portfolio = Portfolio.objects.get(user=user, id=request.data['portfolio'])
                tx_type = TransactionType.objects.get(id=request.data['transactionType'])
                tx_date = request.data['transactionDate']
                tx_amount = request.data['amount']
                tx_price = request.data['price']
                tx_fee = request.data['transactionFee']
                tx_hash_id = request.data['transactionHashId']
                tx_sender_address = request.data['senderAddress']
                tx_recipient_address = request.data['recipientAddress']
                tx_comment = request.data['comment']

                if asset_info is None:
                    return Response(data={'message': 'Kryptowährung wird nicht unterstützt.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                # update asset infos
                self.update_asset_info(asset_info=asset_info)

                # check if asset owned exists in portfolio, if not create owned asset in given portfolio
                asset_in_portfolio = AssetOwned.objects.filter(portfolio__user=user,
                                                               portfolio=portfolio,
                                                               asset=asset_info).first()

                # TODO: Refactor code, check asset_in_portfolio in second if statement and reduce complexity
                if asset_in_portfolio is None:
                    if tx_type.type in ["Staking-Reward", "Kaufen", "Verkaufen", "Gesendet", "Einzahlung", "Auszahlung"]:
                        """
                        add asset to portfolio with current price
                        update portfolio balance
                        create transaction object with price from given datetime
                        """
                        current_price = asset_info.current_price
                        quantity_price = current_price * tx_amount

                        if tx_type.type in ["Verkaufen", "Gesendet", "Auszahlung"]:
                            tx_amount = -tx_amount
                            quantity_price = -quantity_price

                        new_asset_owned = AssetOwned.objects.create(
                            quantity_owned=tx_amount,
                            quantity_price=quantity_price,
                            asset=asset_info,
                            portfolio=portfolio,
                        )
                        portfolio.balance += quantity_price
                        portfolio.save()

                        # get price on tx_date, if error take given tx_price
                        datetime_price = get_historical_price_at_time_coingecko(crypto_id=asset_info.api_id_name,
                                                                                tx_date=tx_date) if asset_info.api_id_name != "euro" else 1.0
                        if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                            if tx_price is None:
                                return Response(
                                    data={'message': 'Preis beim Handel konnte online nicht ermittelt werden, bitte eingeben.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                            datetime_price = tx_price

                        # create transaction with date price and given data and if EURO don't get historical data
                        new_transaction = Transaction.objects.create(
                            user=user,
                            asset=new_asset_owned,
                            tx_type=tx_type,
                            tx_comment=None if not tx_comment else Comment.objects.create(text=tx_comment),
                            tx_hash=tx_hash_id,
                            tx_sender_address=tx_sender_address,
                            tx_recipient_address=tx_recipient_address,
                            tx_amount=tx_amount,
                            tx_value=datetime_price * abs(tx_amount),
                            tx_fee=0.0 if not tx_fee else tx_fee,
                            tx_date=tx_date,
                        )
                    elif tx_type.type == "Handel":
                        """
                        change one currency into another
                        add both assets to chosen portfolio with current price and given data and update portfolio balance
                        subtract old asset quantity, 
                        """
                        if target_asset_info is None:
                            return Response(data={'message': 'Ziel-Kryptowährung wird nicht unterstützt.'},
                                            status=status.HTTP_400_BAD_REQUEST)
                        self.update_asset_info(asset_info=target_asset_info)

                        current_price_old_asset = asset_info.current_price
                        old_asset_owned = AssetOwned.objects.create(
                            quantity_owned=-tx_amount,
                            quantity_price=-(current_price_old_asset * tx_amount),
                            asset=asset_info,
                            portfolio=portfolio,
                        )
                        portfolio.balance += old_asset_owned.quantity_price
                        portfolio.save()

                        current_price_target_asset = target_asset_info.current_price
                        target_asset_amount = convert_crypto_amount(base_crypto=asset_info.api_id_name,
                                                                    target_crypto=target_asset_info.acronym,
                                                                    amount=tx_amount)

                        if not isinstance(target_asset_amount, float) and target_asset_amount.startswith("Fehler"):
                            # conversion unsuccessful due to api error, calculate with given price data
                            if tx_price is None:
                                return Response(
                                    data={'message': 'Preis für die Umrechnung konnte online nicht ermittelt werden, bitte eingeben.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                            target_asset_amount = (tx_price / target_asset_info.current_price) * tx_amount

                        # check if target asset exists in portfolio
                        target_asset_owned = AssetOwned.objects.filter(portfolio__user=user,
                                                                       portfolio=portfolio,
                                                                       asset=target_asset_info).first()
                        if target_asset_owned is None:
                            new_asset_owned = AssetOwned.objects.create(
                                quantity_owned=target_asset_amount,
                                quantity_price=(current_price_target_asset * target_asset_amount),
                                asset=target_asset_info,
                                portfolio=portfolio,
                            )
                            portfolio.balance += new_asset_owned.quantity_price
                            portfolio.save()
                        else:
                            """
                            accumulate quantity_owned with calculated target_asset_amount.
                            get old quantity_price and update quantity_price with new quantity_owned and current price
                            update portfolio balance by subtracting old_asset_owned quantity and adding new quantity
                            """
                            target_asset_owned.quantity_owned += target_asset_amount
                            target_asset_owned.save()
                            old_quantity_price = target_asset_owned.quantity_price
                            target_asset_owned.quantity_price = target_asset_info.current_price * target_asset_owned.quantity_owned
                            target_asset_owned.save()
                            portfolio.balance += target_asset_owned.quantity_price - old_quantity_price
                            portfolio.save()

                        # get price on tx_date, if error take given tx_price
                        datetime_price = get_historical_price_at_time_coingecko(crypto_id=asset_info.api_id_name,
                                                                                tx_date=tx_date) if asset_info.api_id_name != "euro" else 1.0
                        if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                            if tx_price is None:
                                return Response(
                                    data={'message': 'Preis beim Handel konnte online nicht ermittelt werden, bitte eingeben.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                            datetime_price = tx_price

                        # create transaction with date price and given data
                        new_transaction = Transaction.objects.create(
                            user=user,
                            asset=old_asset_owned,
                            tx_type=tx_type,
                            tx_comment=None if not tx_comment else Comment.objects.create(text=tx_comment),
                            tx_hash=tx_hash_id,
                            tx_sender_address=tx_sender_address,
                            tx_recipient_address=tx_recipient_address,
                            tx_amount=tx_amount,
                            tx_value=datetime_price * tx_amount,
                            tx_fee=0.0 if not tx_fee else tx_fee,
                            tx_date=tx_date,
                        )
                    else:
                        return Response(data={'message': 'Kein gültigen Transaktionstyp angegeben.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    if tx_type.type in ["Staking-Reward", "Kaufen", "Verkaufen", "Gesendet", "Einzahlung", "Auszahlung"]:
                        """
                        update asset in portfolio with new quantity and price
                        update portfolio balance
                        create transaction object with price from given datetime
                        """
                        current_price = asset_info.current_price

                        if tx_type.type in ["Verkaufen", "Gesendet", "Auszahlung"]:
                            tx_amount = -tx_amount

                        asset_in_portfolio.quantity_owned += tx_amount
                        asset_in_portfolio.save()
                        old_quantity_price = asset_in_portfolio.quantity_price
                        asset_in_portfolio.quantity_price = current_price * asset_in_portfolio.quantity_owned
                        asset_in_portfolio.save()
                        portfolio.balance += asset_in_portfolio.quantity_price - old_quantity_price
                        portfolio.save()

                        # get price on tx_date, if error take given tx_price
                        datetime_price = get_historical_price_at_time_coingecko(crypto_id=asset_info.api_id_name,
                                                                                tx_date=tx_date) if asset_info.api_id_name != "euro" else 1.0

                        if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                            if tx_price is None:
                                return Response(
                                    data={
                                        'message': 'Preis beim Handel konnte online nicht ermittelt werden, bitte eingeben.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                            datetime_price = tx_price

                        # create transaction with date price and given data and existing asset_in_portfolio
                        new_transaction = Transaction.objects.create(
                            user=user,
                            asset=asset_in_portfolio,
                            tx_type=tx_type,
                            tx_comment=None if not tx_comment else Comment.objects.create(text=tx_comment),
                            tx_hash=tx_hash_id,
                            tx_sender_address=tx_sender_address,
                            tx_recipient_address=tx_recipient_address,
                            tx_amount=tx_amount,
                            tx_value=datetime_price * abs(tx_amount),
                            tx_fee=0.0 if not tx_fee else tx_fee,
                            tx_date=tx_date,
                        )
                    elif tx_type.type == "Handel":
                        """
                        change one currency into another
                        update assets to chosen portfolio with current price and given data and update portfolio balance
                        subtract old asset quantity, accumulate target asset quantity
                        """
                        # check if target asset info exists and update data
                        if target_asset_info is None:
                            return Response(data={'message': 'Ziel-Kryptowährung wird nicht unterstützt.'},
                                            status=status.HTTP_400_BAD_REQUEST)
                        self.update_asset_info(asset_info=target_asset_info)

                        current_price_old_asset = asset_info.current_price
                        current_price_target_asset = target_asset_info.current_price

                        # update existing asset
                        asset_in_portfolio.quantity_owned -= tx_amount
                        asset_in_portfolio.save()
                        old_quantity_price = asset_in_portfolio.quantity_price
                        asset_in_portfolio.quantity_price = current_price_old_asset * asset_in_portfolio.quantity_owned
                        asset_in_portfolio.save()
                        portfolio.balance += asset_in_portfolio.quantity_price - old_quantity_price
                        portfolio.save()

                        # update target asset
                        target_asset_amount = convert_crypto_amount(base_crypto=asset_info.api_id_name,
                                                                    target_crypto=target_asset_info.acronym,
                                                                    amount=tx_amount)

                        if not isinstance(target_asset_amount, float) and target_asset_amount.startswith("Fehler"):
                            # conversion unsuccessful due to api error, calculate with given price data
                            if tx_price is None:
                                return Response(
                                    data={
                                        'message': 'Preis für die Umrechnung konnte online nicht ermittelt werden, bitte eingeben.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                            target_asset_amount = (tx_price / target_asset_info.current_price) * tx_amount

                        # check if target asset exists in portfolio
                        target_asset_owned = AssetOwned.objects.filter(portfolio__user=user,
                                                                       portfolio=portfolio,
                                                                       asset=target_asset_info).first()
                        if target_asset_owned is None:
                            new_asset_owned = AssetOwned.objects.create(
                                quantity_owned=target_asset_amount,
                                quantity_price=(current_price_target_asset * target_asset_amount),
                                asset=target_asset_info,
                                portfolio=portfolio,
                            )
                            portfolio.balance += new_asset_owned.quantity_price
                            portfolio.save()
                        else:
                            """
                            accumulate quantity_owned with calculated target_asset_amount.
                            get old quantity_price and update quantity_price with new quantity_owned and current price
                            update portfolio balance by subtracting old_asset_owned quantity and adding new quantity
                            """
                            target_asset_owned.quantity_owned += target_asset_amount
                            target_asset_owned.save()
                            old_quantity_price = target_asset_owned.quantity_price
                            target_asset_owned.quantity_price = target_asset_info.current_price * target_asset_owned.quantity_owned
                            target_asset_owned.save()
                            portfolio.balance += target_asset_owned.quantity_price - old_quantity_price
                            portfolio.save()

                        # get price on tx_date, if error take given tx_price
                        datetime_price = get_historical_price_at_time_coingecko(crypto_id=asset_info.api_id_name,
                                                                                tx_date=tx_date) if asset_info.api_id_name != "euro" else 1.0

                        if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                            if tx_price is None:
                                return Response(
                                    data={
                                        'message': 'Preis beim Handel konnte online nicht ermittelt werden, bitte eingeben.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                            datetime_price = tx_price

                        # create transaction with date price and given data
                        new_transaction = Transaction.objects.create(
                            user=user,
                            asset=asset_in_portfolio,
                            tx_type=tx_type,
                            tx_comment=None if not tx_comment else Comment.objects.create(text=tx_comment),
                            tx_hash=tx_hash_id,
                            tx_sender_address=tx_sender_address,
                            tx_recipient_address=tx_recipient_address,
                            tx_amount=tx_amount,
                            tx_value=datetime_price * tx_amount,
                            tx_fee=0.0 if not tx_fee else tx_fee,
                            tx_date=tx_date,
                        )
                    else:
                        return Response(data={'message': 'Kein gültigen Transaktionstyp angegeben.'},
                                        status=status.HTTP_400_BAD_REQUEST)

                return Response(data={"message": "Transaktion erfolgreich erstellt."}, status=status.HTTP_201_CREATED)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)


class KrakenFileImportAPIView(APIView):
    """API View for handling csv file data import from crypto exchanges."""
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Asset read in CSV : Asset Acronym for AssetInfo
        self.coin_mapping = {
            'XETH': 'ETH',
            'ETH2.S': 'ETH',
            'ETH2': 'ETH',
            'DOT.S': 'DOT',
            'KAVA.S': 'KAVA',
            'XTZ.S': 'XTZ',
            'ADA.S': 'ADA',
        }

    def post(self, request):
        """POST Route /api/import-file/ for creating new transactions and updating portfolios from csv file"""
        file_obj = request.FILES['csvFile']
        if not file_obj:
            return Response({"error": "Keine Datei hochgeladen."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                '''
                1. Read file, drop columns subtype and aclass, format datetime field
                2. convert asset names from csv column "asset" to predefined asset acronym (symbol) for searching AssetInfo in database
                3. iterate through each line and inspect data
                '''
                # read csv, drop unnecessary columns, format date and convert asset names to acronym
                df = pd.read_csv(file_obj, sep=",")
                df = df.drop(columns=['subtype', 'aclass'])
                df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%dT%H:%M')
                df['asset'] = df['asset'].map(self.coin_mapping).fillna(df['asset'])

                for index, row in df.iterrows():
                    tx_id = row["txid"]
                    tx_refid = row["refid"]
                    tx_time = row["time"]
                    tx_type = row["type"]
                    tx_asset_acronym = row["asset"]
                    tx_fee = row["fee"]
                    tx_balance = row["balance"]
                    asset_info = AssetInfo.objects.filter(acronym=tx_asset_acronym).first()
                    if asset_info is not None:
                        print(asset_info)
                    else:
                        print(f"{tx_asset_acronym} nicht gefunden")

                # create transaction with date price and given data
                # new_transaction = Transaction.objects.create(
                #     user=user,
                #     asset=asset_in_portfolio,
                #     tx_type=tx_type,
                #     tx_comment=None if not tx_comment else Comment.objects.create(text=tx_comment),
                #     tx_hash=tx_hash_id,
                #     tx_sender_address=tx_sender_address,
                #     tx_recipient_address=tx_recipient_address,
                #     tx_amount=tx_amount,
                #     tx_value=datetime_price * tx_amount,
                #     tx_fee=0.0 if not tx_fee else tx_fee,
                #     tx_date=tx_date,
                # )

                return Response(df.head().to_json(orient='records'), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
