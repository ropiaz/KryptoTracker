# Author: Roberto Piazza
# Date: 25.03.2023
from pathlib import Path

# models import and django auth functions
from django.db.models import Q
from .models import PortfolioType, Portfolio, AssetInfo, AssetOwned, Comment, TransactionType, Transaction, TaxReport, ExchangeAPIs
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import FileResponse
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
import requests
import io
import os
from xhtml2pdf import pisa


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
    def update_asset_info(self, asset_info, portfolio):
        """Update asset info image and current price if last updated is > 30min. If CoinGecko fails use webscraping and get data from coinmarkecap"""
        if asset_info.api_id_name == 'euro':
            return

        current_time = timezone.now()
        time_delta = timedelta(minutes=180)
        if current_time - asset_info.updated_at < time_delta and asset_info.current_price != 0.0:
            # print(f"{asset_info.fullname} wurde vor weniger als 30 Minuten aktualisiert.")
            return

        def update_balances(asset, user_portfolio):
            print("update balances")
            # update portfolio balance and asset owned quantity
            asset_owned = AssetOwned.objects.filter(asset=asset, portfolio=user_portfolio).first()
            old_quantity_price = asset_owned.quantity_price
            asset_owned.quantity_price = asset.current_price * asset_owned.quantity_owned
            asset_owned.save()
            user_portfolio.balance += asset_owned.quantity_price - old_quantity_price
            user_portfolio.save()

        try:
            # get data from coingecko api
            new_data = get_currency_data(api_id_name=asset_info.api_id_name)
            asset_info.current_price = new_data['current_price']
            asset_info.image = new_data['image']
            asset_info.save()
            update_balances(asset=asset_info, user_portfolio=portfolio)
        except:
            # get data from webscraping coinmarketcap
            data = get_crypto_data_from_coinmarketcap(crypto_name=asset_info.api_id_name)
            asset_info.current_price = data['current_price']
            asset_info.image = data['image']
            asset_info.save()
            update_balances(asset=asset_info, user_portfolio=portfolio)

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
                    self.update_asset_info(asset_info=own.asset, portfolio=portfolio)
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

    def get_chart_data(self, user, asset_infos):
        """Return all owned assets with acronym and their value in euro."""
        # get all owned assets from all portfolios that belongs to a user
        asset_owned = AssetOwned.objects.filter(portfolio__user=user, asset__in=asset_infos)

        assets_sum = {}
        for owned in asset_owned:
            asset_acronym = owned.asset.acronym.upper()
            if asset_acronym in assets_sum:
                # add the value to the existing asset
                assets_sum[asset_acronym] += round(owned.quantity_price, 3)
            else:
                # add new asset to the dictionary
                assets_sum[asset_acronym] = round(owned.quantity_price, 3)

        # create a list of dictionaries from the assets_sum dictionary
        data = [{'asset': asset, 'EUR': value} for asset, value in assets_sum.items()]

        # sort list ASC
        sorted_data = sorted(data, key=lambda x: x['EUR'], reverse=True)

        return sorted_data

    def get_tax_data(self, user):
        """get and return tax data for dashboard"""
        tax_reports = TaxReport.objects.filter(user=user).order_by('-year', '-created_at')
        tax_data_list = []
        for report in tax_reports:
            time_period = str(report.year) if report.year else f"{report.start_date.strftime('%d.%m.%Y')} bis {report.end_date.strftime('%d.%m.%Y')}"

            tax_data_list.append({
                'id': report.id,
                'time_period': time_period,
                'income_trading': report.income_trading,
                'income_staking': report.income_staking,
                'created_at': report.created_at.strftime('%d.%m.%Y %H:%M'),
                'updated_at': report.updated_at.strftime('%d.%m.%Y %H:%M'),
            })

        return tax_data_list

    def get(self, request):
        """GET Route /api/dashboard for dashboard"""
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                # get owned assets
                portfolios = Portfolio.objects.filter(user=user)
                portfolio_serializer = PortfolioSerializer(portfolios, many=True)
                asset_owned = AssetOwned.objects.filter(portfolio__in=portfolios)
                asset_owned_serializer = AssetOwnedSerializer(asset_owned, many=True)
                count_asset_owned = len(asset_owned_serializer.data)

                # get balances from portfolios
                sum_balance, spot_balance, staking_balance = self.get_balances(portfolio_serializer.data)

                # get all transactions and extract necessary data
                count_transactions, first_transaction_formatted, last_transaction_formatted, last_five_transactions = self.get_transactions_data(user=user)

                # get all asset infos from database
                asset_infos = AssetInfo.objects.all()

                # get the user related balances (assets in spot and staking)
                all_portfolios_data = self.get_assets_in_portfolios(user, asset_infos)

                # get chart data
                chart_data = self.get_chart_data(user, asset_infos)

                # get tax data
                tax_data = self.get_tax_data(user=user)

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
                    'tax_data': tax_data
                }
                return Response(data=context, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response(data={'detail': 'Ungültiges Token.'}, status=status.HTTP_400_BAD_REQUEST)


class AssetOwnedAPIView(APIView):
    """API View for handling CRUD operations on AssetOwned model."""
    authentication_classes = [TokenAuthentication]

    def update_asset_info(self, asset_info):
        """Update asset info image and current price if last updated is > 30min. If CoinGecko fails use webscraping and get data from coinmarkecap"""
        if asset_info.api_id_name == 'euro':
            return

        current_time = timezone.now()
        time_delta = timedelta(minutes=30)
        if current_time - asset_info.updated_at < time_delta and asset_info.current_price != 0.0:
            # print(f"{asset_info.fullname} wurde vor weniger als 30 Minuten aktualisiert.")
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
        """Return only id, name, balance, type"""
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
                    'tx_id': tx['id'],
                    'tx_type': tx_type.type,
                    'asset': asset_owned.asset.acronym.upper(),
                    'tx_amount': str(round(tx['tx_amount'], 3)).replace('.', ','),
                    'tx_value': str(round(tx['tx_value'], 3)).replace('.', ','),
                    'tx_fee': str(round(tx['tx_fee'], 3)).replace('.', ','),
                    'tx_date': tx_date_formatted,
                    'tx_hash': tx['tx_hash'],
                    'tx_status': 'In Bearbeitung' if tx['status'] == 0 else 'Abgeschlossen',
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
    # TODO: set transaction status true if price is available, otherwise false and queuing
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
                    if tx_type.type in ["Reward", "Kaufen", "Verkaufen", "Gesendet", "Einzahlung", "Auszahlung"]:
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
                    if tx_type.type in ["Reward", "Kaufen", "Verkaufen", "Gesendet", "Einzahlung", "Auszahlung"]:
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


class TransactionDetailAPIView(APIView):
    """Retrieve, update or delete a transaction instance."""
    def get_object(self, pk):
        try:
            return Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return Response(data={'error': 'Transaktion nicht gefunden.'}, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, pk):
    #     transaction = self.get_object(pk)
    #     serializer = TransactionSerializer(snippet, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # TODO: decrease asset / portfolio volume when deleting transcation?
    def delete(self, request, pk):
        transaction = self.get_object(pk)
        transaction.delete()
        return Response(data={'message': 'success'}, status=status.HTTP_204_NO_CONTENT)


class KrakenFileImportAPIView(APIView):
    """API View for handling csv file data import from crypto exchanges."""
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coin_mapping = {
            'ADA.S':     'ADA',
            'ALGO.S':    'ALGO',
            'ATOM.S':    'ATOM',
            'ATOM21.S':  'ATOM',
            'DOT.S':     'DOT',
            'DOT28.S':   'DOT',
            'ETH2':      'ETH',
            'ETH2.S':    'ETH',
            'ETHW':      'ETH',
            'FLOW.S':    'FLOW',
            'FLOW14.S':  'FLOW',
            'FLOWH.S':   'FLOW',
            'FLR.S':     'FLR',
            'GRT.S':     'GRT',
            'GRT28.S':   'GRT',
            'KAVA.S':    'KAVA',
            'KAVA21.S':  'KAVA',
            'KSM.S':     'KSM',
            'KSM07.S':   'KSM',
            'LUNA.S':    'LUNA',
            'MATIC.S':   'MATIC',
            'MATIC04.S': 'MATIC',
            'MINA.S':    'MINA',
            'SCRT.S':    'SCRT',
            'SCRT21.S':  'SCRT',
            'SOL.S':     'SOL',
            'SOL03.S':   'SOL',
            'USDC.M':    'USDC',
            'USDT.M':    'USDT',
            'XBT.M':     'XBT',
            'TRX.S':     'TRX',
            'XBT':       'BTC',
            'XETC':      'ETC',
            'XETH':      'ETH',
            'XTZ.S':     'XTZ',
            'XLTC':      'LTC',
            'XMLN':      'MLN',
            'XREP':      'REP',
            'XXBT':      'BTC',
            'XXDG':      'XDG',
            'XXLM':      'XLM',
            'XXMR':      'XMR',
            'XXRP':      'XRP',
            'XZEC':      'ZEC',
            'ZAUD':      'AUD',
            'ZCAD':      'CAD',
            'ZEUR':      'EUR',
            'ZGBP':      'GBP',
            'ZJPY':      'JPY',
            'ZUSD':      'USD',
        }

        self.type_mapping = {
            'trade':      'Handel',
            'deposit':    'Einzahlung',
            'withdrawal': 'Gesendet',
            'staking':    'Reward',
            'earn':       'Reward',
            'buy':        'Kaufen',
            'sell':       'Verkaufen',
            'transfer':   'Transfer'
        }

    def get_coin_pairs(self, dataframe):
        pairs = set([row['pair'] for index, row in dataframe.iterrows()])
        joined_pairs_list = ",".join(pairs)
        url = f'https://api.kraken.com/0/public/AssetPairs?pair={joined_pairs_list}'
        response = requests.get(url)
        if response.status_code != 200:
            return 'Fehler beim Abrufen der Daten von der API'

        data = response.json()['result']
        return data

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

    def create_asset_update_portfolio(self, asset_owned: AssetOwned, asset_info: AssetInfo, portfolio: Portfolio,
                                      balance: float, quantity_price: float, amount: float, tx_exists: bool = False):
        if asset_owned is None:
            asset_owned = AssetOwned.objects.create(
                quantity_owned=balance,
                quantity_price=quantity_price,
                asset=asset_info,
                portfolio=portfolio,
            )
            portfolio.balance += quantity_price
            portfolio.save()
        else:
            asset_owned.quantity_owned = balance
            # asset_owned.quantity_owned += amount
            asset_owned.save()
            old_quantity_price = asset_owned.quantity_price
            asset_owned.quantity_price = asset_info.current_price * asset_owned.quantity_owned
            asset_owned.save()
            portfolio.balance += asset_owned.quantity_price - old_quantity_price
            portfolio.save()

        return asset_owned

    def create_tx(self, asset_owned: AssetOwned, asset_info: AssetInfo, portfolio: Portfolio,  user: User, element, amount: float, tx_type: str):
        tx_fee = element['fee_ledgers']
        tx_date = element['time_ledgers']
        asset = element['asset']
        if tx_type in ["Kaufen", "Verkaufen"]:
            tx_fee = element['fee_trades']
            tx_date = element['time_trades']
            asset = element['base']
            if tx_type in ['Verkaufen']:
                amount = -amount

        datetime_price = element['amount'] # TODO: correct standard value?
        if asset != 'EUR':
            # get price on tx_date with coingecko, if error try cryotocompare api otherwise 0.0 and TODO: update later
            datetime_price = get_historical_price_at_time_coingecko(crypto_id=asset_info.api_id_name,
                                                                    tx_date=tx_date) if asset_info.api_id_name != "euro" else 1.0
            if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                datetime_price = get_historical_price_at_time(tx_date=tx_date,
                                                              crypto_symbol=asset) if asset_info.api_id_name != "euro" else 1.0
                if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                    datetime_price = 0.0

        type_tx = TransactionType.objects.get(type=tx_type)
        comment_text = f"{portfolio.name}-Import: {amount} {asset}"
        comment = Comment.objects.create(text=comment_text)
        Transaction.objects.create(
            user=user,
            asset=asset_owned,
            tx_type=type_tx,
            tx_comment=comment,
            tx_hash=element['txid'],
            tx_amount=amount,
            tx_value=datetime_price * amount if asset != 'EUR' else amount,
            tx_fee=tx_fee,
            tx_date=tx_date,
            status=False if datetime_price == 0.0 else True
        )

    def processing_trades_csv(self, dataframe, data):
        pair_separated = {}
        # assign pairs to their originals coins in a dict e.g. { 'ADAEUR': {'base': 'ADA', 'quote': 'EUR} }
        for k, v in data.items():
            pairs = v['wsname'].split('/')
            base = pairs[0]  # target coin
            quote = pairs[1]  # source coin
            pair_separated[k] = {'base': base, 'quote': quote}

        def assign_base_quote(row, pairs_separated):
            row['base'] = pairs_separated[row['pair']]['base']
            row['quote'] = pairs_separated[row['pair']]['quote']
            return row

        dataframe = dataframe.apply(lambda row: assign_base_quote(row, pair_separated), axis=1)
        dataframe['base'] = dataframe['base'].map(self.coin_mapping).fillna(dataframe['base'])
        dataframe['quote'] = dataframe['quote'].map(self.coin_mapping).fillna(dataframe['quote'])

        return dataframe

    def post(self, request):
        """POST Route /api/import-file/ for creating new transactions and updating portfolios from csv file"""
        csv_file = request.FILES['csvFile']
        csv_file2 = request.FILES['csvFile2']
        if not csv_file or not csv_file2:
            return Response({"error": "Keine Datei hochgeladen."}, status=status.HTTP_400_BAD_REQUEST)

        print(csv_file, csv_file2)

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
                df = pd.read_csv(csv_file, sep=",")
                df_ledgers = pd.read_csv(csv_file2, sep=",")

                error_msg = ""
                if "pair" not in df.columns and "ordertxid" not in df.columns:
                    error_msg += "trades.csv Dateiexport nicht akzeptiert.\n"
                if "refid" not in df_ledgers.columns and "asset" not in df_ledgers.columns:
                    error_msg += "ledgers.csv Dateiexport nicht akzeptiert."

                if error_msg != "":
                    return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

                count_rows = len(df.index)
                count_rows_ledgers = len(df_ledgers.index)
                if count_rows == 0 and count_rows_ledgers == 0:
                    return Response({"message": "CSV-Exporte enthalten keine Einträge."},
                                    status=status.HTTP_202_ACCEPTED)

                if count_rows > 0:
                    # format dataframe columns of trades.csv
                    df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%dT%H:%M')
                    df = df.drop(columns=['ordertype', 'margin', 'misc', 'ledgers'])
                    df['type'] = df['type'].map(self.type_mapping).fillna(df['type'])
                    df.insert(loc=3, column='base', value="")
                    df.insert(loc=4, column='quote', value="")

                    data = self.get_coin_pairs(dataframe=df)
                    if not isinstance(data, dict) and data.startswith("Fehler"):
                        return Response(
                            data={
                                'message': 'Kryptopaare konnten online nicht ermittelt werden. Versuche es später erneut'},
                            status=status.HTTP_400_BAD_REQUEST)
                    df = self.processing_trades_csv(dataframe=df, data=data)

                if count_rows_ledgers > 0:
                    # format dataframe columns of ledgers.csv
                    df_ledgers['time'] = pd.to_datetime(df_ledgers['time']).dt.strftime('%Y-%m-%dT%H:%M')
                    df_ledgers = df_ledgers.drop(columns=['aclass'])
                    df_ledgers['asset'] = df_ledgers['asset'].map(self.coin_mapping).fillna(df_ledgers['asset'])
                    df_ledgers['type'] = df_ledgers['type'].map(self.type_mapping).fillna(df_ledgers['type'])

                    # dataframe contains columns where 'txid' and 'balance' are not NaN and additionally 'subtype' is not NaN
                    condition1 = pd.notna(df_ledgers['txid']) & pd.notna(df_ledgers['balance']) & pd.notna(df_ledgers['subtype'])
                    # dataframe contains columns where 'txid' and 'balance' are not NaN
                    condition2 = pd.notna(df_ledgers['txid']) & pd.notna(df_ledgers['balance'])
                    final_condition = condition1 | condition2
                    df_ledgers = df_ledgers[final_condition]

                # print(df)
                # print(df_ledgers)

                # merge trades and ledgers dataframe
                full_merged_df = pd.merge(df_ledgers, df, on='txid', how='outer', suffixes=('_ledgers', '_trades'))
                print(full_merged_df)

                portfolio_type_spot = PortfolioType.objects.filter(type="Spot").first()
                portfolio_type_staking = PortfolioType.objects.filter(type="Staking").first()

                # check if user has staking and spot portfolio with name "Kraken"
                portfolio_spot = Portfolio.objects.filter(user=user,
                                                          portfolio_type=portfolio_type_spot,
                                                          name="Kraken").first()
                portfolio_staking = Portfolio.objects.filter(user=user,
                                                             portfolio_type=portfolio_type_staking,
                                                             name="Kraken").first()

                if "Reward" in full_merged_df['type_ledgers'].values and portfolio_staking is None:
                    portfolio_staking = Portfolio.objects.create(user=user,
                                                                 name='Kraken',
                                                                 balance=0.0,
                                                                 portfolio_type=portfolio_type_staking)
                if portfolio_spot is None:
                    portfolio_spot = Portfolio.objects.create(user=user,
                                                              name='Kraken',
                                                              balance=0.0,
                                                              portfolio_type=portfolio_type_spot)

                not_found = []
                for index, element in full_merged_df.iterrows():
                    print(index)
                    tx_exists = Transaction.objects.filter(user=user, tx_hash=element['txid']).exists()
                    if tx_exists:
                        continue

                    asset_info = AssetInfo.objects.filter(acronym=element["asset"]).first()
                    asset_info_trades = AssetInfo.objects.filter(acronym=element["base"]).first() if count_rows > 0 else None

                    if count_rows_ledgers > 0:
                        if element['asset'] == 'USD' and asset_info is None:
                            asset_info = AssetInfo.objects.filter(acronym='USDT').first()
                    if count_rows > 0:
                        if element['base'] == 'USD' and asset_info_trades is None:
                            asset_info_trades = AssetInfo.objects.filter(acronym='USDT').first()

                    if asset_info is None and asset_info_trades is None:
                        # print(f"{tx_asset_acronym} nicht gefunden")
                        not_found.append({
                            'txid': element["txid"],
                            'refid': element["refid"],
                            'time': element["time_ledgers"],
                            'type': element["type_ledgers"],
                            'subtype': element["subtype"],
                            'asset': element["asset"],
                            'fee': element["fee_ledgers"],
                            'balance': element["balance"]
                        })
                        continue
                    else:
                        amount = element['amount']
                        balance = element['balance']
                        # quantity_price = amount * asset_info.current_price if asset_info is not None else amount * asset_info_trades.current_price if asset_info_trades is not None else 0.0

                        if asset_info is not None and asset_info_trades is None:
                            self.update_asset_info(asset_info=asset_info)
                            quantity_price = amount * asset_info.current_price
                        if asset_info_trades is not None and asset_info is None:
                            self.update_asset_info(asset_info=asset_info_trades)

                        if element['type_ledgers'] == "Reward":
                            asset_owned = AssetOwned.objects.filter(asset=asset_info,
                                                                    portfolio=portfolio_staking).first()
                            asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                                                                             asset_info=asset_info,
                                                                             portfolio=portfolio_staking,
                                                                             amount=amount,
                                                                             balance=balance,
                                                                             quantity_price=quantity_price)
                            self.create_tx(asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_staking,
                                           element=element, amount=amount, user=user, tx_type=element['type_ledgers'])
                        elif element['type_ledgers'] in ['Einzahlung']:
                            asset_owned = AssetOwned.objects.filter(asset=asset_info,
                                                                    portfolio=portfolio_spot).first()
                            asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                                                                             asset_info=asset_info,
                                                                             portfolio=portfolio_spot,
                                                                             amount=amount,
                                                                             balance=balance,
                                                                             quantity_price=quantity_price)
                            self.create_tx(asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_spot,
                                           element=element, amount=amount, user=user, tx_type=element['type_ledgers'])
                        elif element['type_ledgers'] in ['Transfer']:
                            # handle transfers between spot, futures and staking portfolio
                            '''spotfromstaking, stakingtospot, -- stakingfromspot, spottostaking, -- spottofutures, spotfromfutures'''
                            if element['subtype'] in ['spottostaking', 'spotfromstaking', 'spottofutures', 'spotfromfutures']:
                                asset_owned = AssetOwned.objects.filter(asset=asset_info,
                                                                        portfolio=portfolio_spot).first()
                                asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                                                                                 asset_info=asset_info,
                                                                                 portfolio=portfolio_spot,
                                                                                 amount=amount,
                                                                                 balance=balance,
                                                                                 quantity_price=quantity_price)
                                self.create_tx(asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_spot,
                                               element=element, amount=amount, user=user, tx_type=element['type_ledgers'])
                            elif element['subtype'] in ['stakingfromspot', 'stakingtospot']:
                                asset_owned = AssetOwned.objects.filter(asset=asset_info, portfolio=portfolio_staking).first()
                                asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                                                                                 asset_info=asset_info,
                                                                                 portfolio=portfolio_staking,
                                                                                 amount=amount,
                                                                                 balance=balance,
                                                                                 quantity_price=quantity_price)
                                self.create_tx(asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_staking,
                                               user=user, element=element, amount=amount, tx_type=element['type_ledgers'])
                            elif amount > 0.0 or amount < 0.0:
                                asset_owned = AssetOwned.objects.filter(asset=asset_info,
                                                                        portfolio=portfolio_spot).first()
                                asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                                                                                 asset_info=asset_info,
                                                                                 portfolio=portfolio_spot,
                                                                                 amount=amount,
                                                                                 balance=balance,
                                                                                 quantity_price=quantity_price)
                                self.create_tx(asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_spot,
                                               user=user, element=element, amount=amount, tx_type=element['type_ledgers'])
                            else:
                                not_found.append({
                                    'txid': element["txid"],
                                    'refid': element["refid"],
                                    'time': element["time_ledgers"],
                                    'type': element["type_ledgers"],
                                    'subtype': element["subtype"],
                                    'asset': element["asset"],
                                    'fee': element["fee_ledgers"],
                                    'balance': element["balance"]
                                })
                                continue
                        elif element['type_ledgers'] in ['Handel']:
                            asset_owned = AssetOwned.objects.filter(asset=asset_info,
                                                                    portfolio=portfolio_spot).first()
                            tx_exist = Transaction.objects.filter(user=user, tx_hash=element['refid']).exists()

                            asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                                                                             asset_info=asset_info,
                                                                             portfolio=portfolio_spot,
                                                                             amount=amount,
                                                                             balance=balance,
                                                                             quantity_price=quantity_price,
                                                                             tx_exists=tx_exist)
                            self.create_tx(asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_spot,
                                           user=user, element=element, amount=amount, tx_type=element['type_ledgers'])
                        elif element['type_ledgers'] in ['Gesendet']:
                            asset_owned = AssetOwned.objects.filter(asset=asset_info,
                                                                    portfolio=portfolio_spot).first()
                            asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                                                                             asset_info=asset_info,
                                                                             portfolio=portfolio_spot,
                                                                             amount=amount,
                                                                             balance=balance,
                                                                             quantity_price=quantity_price)
                            self.create_tx(asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_spot,
                                           user=user, element=element, amount=amount, tx_type=element['type_ledgers'])
                        elif element['type_trades'] in ['Kaufen', 'Verkaufen']:
                            asset_owned = AssetOwned.objects.filter(asset=asset_info_trades,
                                                                    portfolio=portfolio_spot).first()
                            amount = element['vol']
                            self.create_tx(asset_info=asset_info_trades, asset_owned=asset_owned, portfolio=portfolio_spot,
                                           user=user, element=element, amount=amount, tx_type=element['type_trades'])

                #######################################################################################################

                # check if it's trades or ledgers csv export
                # if "pair" in df.columns and "ordertxid" in df.columns:
                #     # it's trades.csv
                #     print("trades csv")
                #     '''
                #     format dataframe:
                #     - drop unnecessary columns,
                #     - map types with TransactionType,
                #     - split pairs column in base (target asset) and quote (source asset) and insert into dataframe.
                #     - get or create 'Kraken' Spot Portfolio and iterate through dataframe
                #     '''
                #     df = df.drop(columns=['ordertype', 'margin', 'misc', 'ledgers'])
                #     df['type'] = df['type'].map(self.type_mapping).fillna(df['type'])
                #     df.insert(loc=3, column='base', value="")
                #     df.insert(loc=4, column='quote', value="")
                #
                #     data = self.get_coin_pairs(dataframe=df)
                #     if not isinstance(data, dict) and data.startswith("Fehler"):
                #         return Response(
                #             data={
                #                 'message': 'Kryptopaare konnten online nicht ermittelt werden. Versuche es später erneut'},
                #             status=status.HTTP_400_BAD_REQUEST)
                #
                #     pair_separated = {}
                #     # assign pairs to their originals coins in a dict e.g. { 'ADAEUR': {'base': 'ADA', 'quote': 'EUR} }
                #     for k, v in data.items():
                #         pairs = v['wsname'].split('/')
                #         base = pairs[0]   # target coin
                #         quote = pairs[1]  # source coin
                #         pair_separated[k] = {'base': base, 'quote': quote}
                #
                #     def assign_base_quote(row, pairs_separated):
                #         row['base'] = pairs_separated[row['pair']]['base']
                #         row['quote'] = pairs_separated[row['pair']]['quote']
                #         return row
                #
                #     df = df.apply(lambda row: assign_base_quote(row, pair_separated), axis=1)
                #     df['base'] = df['base'].map(self.coin_mapping).fillna(df['base'])
                #     df['quote'] = df['quote'].map(self.coin_mapping).fillna(df['quote'])
                #
                #     # check if Spot portfolio exist, if not create one
                #     portfolio_type_spot = PortfolioType.objects.filter(type="Spot").first()
                #     portfolio = Portfolio.objects.filter(user=user,
                #                                          portfolio_type=portfolio_type_spot,
                #                                          name='Kraken').first()
                #
                #     if portfolio is None:
                #         portfolio = Portfolio.objects.create(user=user,
                #                                              name='Kraken',
                #                                              balance=0.0,
                #                                              portfolio_type=portfolio_type_spot)
                #
                #     print(df)
                #
                #     for idx, element in df.iterrows():
                #         '''
                #         - if Kraken TX-ID exists, continue (then it's already imported)
                #         - get base and quote asset and update values (current price)
                #         - if quote != EUR, get historical price from asset otherwise take from csv data
                #         - check if assets exist in portfolio, if not create AssetOwned
                #             - case buy: increase base asset balance and decrease quote asset balance, update portfolio
                #             - case sell decrease base asset balance and increase quote asset balance, update portfolio
                #         - create transaction
                #         '''
                #         tx_exists = Transaction.objects.filter(user=user, tx_hash=element['txid']).exists()
                #         if tx_exists:
                #             continue
                #
                #         print(idx)
                #
                #         asset_info_base = AssetInfo.objects.filter(acronym=element['base']).first()
                #         asset_info_quote = AssetInfo.objects.filter(acronym=element['quote']).first()
                #
                #         if element['base'] == 'USD' and asset_info_base is None:
                #             asset_info_base = AssetInfo.objects.filter(acronym='USDT').first()
                #         if element['quote'] == 'USD' and asset_info_quote is None:
                #             asset_info_quote = AssetInfo.objects.filter(acronym='USDT').first()
                #
                #         if asset_info_base is not None and asset_info_quote is not None:
                #             self.update_asset_info(asset_info=asset_info_base)
                #             self.update_asset_info(asset_info=asset_info_quote)
                #
                #         asset_owned = AssetOwned.objects.filter(asset=asset_info_base, portfolio=portfolio).first()
                #
                #         datetime_price = element['price']
                #         if element['quote'] != 'EUR':
                #             # get price on tx_date with coingecko, if error try cryotocompare api otherwise 0.0 and TODO: update later
                #             datetime_price = get_historical_price_at_time_coingecko(crypto_id=asset_info_base.api_id_name,
                #                                                                     tx_date=element['time']) if asset_info_base.api_id_name != "euro" else 1.0
                #             if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                #                 datetime_price = get_historical_price_at_time(tx_date=element['time'],
                #                                                               crypto_symbol=element['base']) if asset_info_base.api_id_name != "euro" else 1.0
                #                 if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                #                     datetime_price = 0.0
                #
                #         if element['type'] in ['Kaufen', 'Verkaufen']:
                #             current_price = asset_info_base.current_price
                #             amount = element['vol']
                #             quantity_price = current_price * amount
                #
                #             # in case of buy decrease quote asset
                #             amount_quote = -element['cost']
                #             quantity_price_quote = asset_info_quote.current_price * amount_quote
                #
                #             if element['type'] in ['Verkaufen']:
                #                 amount = -amount
                #                 quantity_price = -quantity_price
                #                 amount_quote = -amount_quote
                #                 quantity_price_quote = -quantity_price_quote
                #
                #             # handle the base asset. case buy: increase balance, case sell: decrease balance,
                #             # if asset_owned is None:
                #             #     asset_owned = AssetOwned.objects.create(
                #             #         quantity_owned=amount,
                #             #         quantity_price=quantity_price,
                #             #         asset=asset_info_base,
                #             #         portfolio=portfolio,
                #             #     )
                #                 # portfolio.balance += quantity_price
                #                 # portfolio.save()
                #             # else:
                #                 # asset_owned.quantity_owned += amount
                #                 # asset_owned.save()
                #                 # old_quantity_price = asset_owned.quantity_price
                #                 # asset_owned.quantity_price = current_price * asset_owned.quantity_owned
                #                 # asset_owned.save()
                #                 # portfolio.balance += asset_owned.quantity_price - old_quantity_price
                #                 # portfolio.save()
                #
                #             # asset_owned_quote = AssetOwned.objects.filter(asset=asset_info_quote,
                #             #                                               portfolio=portfolio).first()
                #
                #             # handle the quote asset. case buy: decrease balance, case sell: increase balance,
                #             # if asset_owned_quote is None:
                #             #     asset_owned_quote = AssetOwned.objects.create(
                #             #         quantity_owned=amount_quote,
                #             #         quantity_price=quantity_price_quote,
                #             #         asset=asset_info_quote,
                #             #         portfolio=portfolio,
                #             #     )
                #             #     portfolio.balance += quantity_price_quote
                #             #     portfolio.save()
                #             # else:
                #             #     asset_owned_quote.quantity_owned += amount_quote
                #             #     asset_owned_quote.save()
                #             #     old_quantity_price = asset_owned_quote.quantity_price
                #             #     asset_owned_quote.quantity_price = asset_info_quote.current_price * asset_owned_quote.quantity_owned
                #             #     asset_owned_quote.save()
                #             #     portfolio.balance += asset_owned_quote.quantity_price - old_quantity_price
                #             #     portfolio.save()
                #
                #             tx_type = TransactionType.objects.get(type=element['type'])
                #             comment_buy = f"{portfolio.name}-Import: {element['base']} mit {element['quote']}"
                #             comment_sell = f"{portfolio.name}-Import: {element['base']} in {element['quote']}"
                #             comment = Comment.objects.create(text=comment_buy if tx_type.type == 'Kaufen' else comment_sell)
                #             transaction = Transaction.objects.create(
                #                 user=user,
                #                 asset=asset_owned,
                #                 tx_type=tx_type,
                #                 tx_comment=comment,
                #                 tx_hash=element['txid'],
                #                 tx_amount=amount,
                #                 tx_value=datetime_price * amount if element['quote'] != 'EUR' else element['cost'],
                #                 tx_fee=float(element['fee']),
                #                 tx_date=element['time'],
                #                 status=False if datetime_price == 0.0 else True
                #             )
                # elif "refid" in df.columns and "asset" in df.columns:
                #     # it's ledgers.csv
                #     '''
                #     format dataframe:
                #     - drop unnecessary columns and rows with NaN rows (these are doubled)
                #         - filter dataframe where txid, balance, subtype are not NaN or txid and balance are not NaN
                #     - map types with TransactionType and assets,
                #     - get or create 'Kraken' Spot Portfolio and iterate through dataframe
                #     '''
                #     print("ledgers csv")
                #
                #     df = df.drop(columns=['aclass'])
                #     df['asset'] = df['asset'].map(self.coin_mapping).fillna(df['asset'])
                #     df['type'] = df['type'].map(self.type_mapping).fillna(df['type'])
                #
                #     # dataframe contains columns where 'txid' and 'balance' are not NaN and additionally 'subtype' is not NaN
                #     condition1 = pd.notna(df['txid']) & pd.notna(df['balance']) & pd.notna(df['subtype'])
                #     # dataframe contains columns where 'txid' and 'balance' are not NaN
                #     condition2 = pd.notna(df['txid']) & pd.notna(df['balance'])
                #     final_condition = condition1 | condition2
                #     df = df[final_condition]
                #
                #     print(df)
                #
                #     portfolio_type_spot = PortfolioType.objects.filter(type="Spot").first()
                #     portfolio_type_staking = PortfolioType.objects.filter(type="Staking").first()
                #
                #     # check if user has staking and spot portfolio with name "Kraken"
                #     portfolio_spot = Portfolio.objects.filter(user=user,
                #                                               portfolio_type=portfolio_type_spot,
                #                                               name="Kraken").first()
                #     portfolio_staking = Portfolio.objects.filter(user=user,
                #                                                  portfolio_type=portfolio_type_staking,
                #                                                  name="Kraken").first()
                #
                #     if "Reward" in df['type'].values and portfolio_staking is None:
                #         portfolio_staking = Portfolio.objects.create(user=user,
                #                                                      name='Kraken',
                #                                                      balance=0.0,
                #                                                      portfolio_type=portfolio_type_staking)
                #     if portfolio_spot is None:
                #         portfolio_spot = Portfolio.objects.create(user=user,
                #                                                   name='Kraken',
                #                                                   balance=0.0,
                #                                                   portfolio_type=portfolio_type_spot)
                #
                #     not_found = []
                #     for index, element in df.iterrows():
                #         # print(index)
                #         tx_exists = Transaction.objects.filter(user=user, tx_hash=element['txid']).exists()
                #         if tx_exists:
                #             continue
                #
                #         # start_time = datetime.strptime('2022-09-23 06:22:22', '%Y-%m-%d %H:%M:%S')
                #         # end_time = datetime.strptime('2022-09-23 06:33:17', '%Y-%m-%d %H:%M:%S')
                #         # element_time = datetime.strptime(element['time'], '%Y-%m-%dT%H:%M')
                #         #
                #         # if element_time < start_time or element_time > end_time:
                #         #     continue
                #
                #         asset_info = AssetInfo.objects.filter(acronym=element["asset"]).first()
                #
                #         if element['asset'] == 'USD' and asset_info is None:
                #             asset_info = AssetInfo.objects.filter(acronym='USDT').first()
                #
                #         if asset_info is None:
                #             # print(f"{tx_asset_acronym} nicht gefunden")
                #             not_found.append({
                #                 'txid': element["txid"],
                #                 'tx_refid': element["refid"],
                #                 'time': element["time"],
                #                 'type': element["type"],
                #                 'subtype': element["subtype"],
                #                 'asset': element["asset"],
                #                 'fee': element["fee"],
                #                 'balance': element["balance"]
                #             })
                #             continue
                #         else:
                #             print(index)
                #             self.update_asset_info(asset_info=asset_info)
                #
                #             amount = element['amount']
                #             balance = element['balance']
                #             quantity_price = amount * asset_info.current_price
                #
                #             if element["type"] == "Reward":
                #                 asset_owned = AssetOwned.objects.filter(asset=asset_info,
                #                                                         portfolio=portfolio_staking).first()
                #                 asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                #                                                                  asset_info=asset_info,
                #                                                                  portfolio=portfolio_staking,
                #                                                                  amount=amount,
                #                                                                  balance=balance,
                #                                                                  quantity_price=quantity_price)
                #                 self.create_tx(asset_info=asset_info, asset_owned=asset_owned, user=user,
                #                                element=element, amount=amount, portfolio=portfolio_staking)
                #             elif element['type'] in ['Einzahlung']:
                #                 # todo: check if withdrawal is here too
                #                 asset_owned = AssetOwned.objects.filter(asset=asset_info,
                #                                                         portfolio=portfolio_spot).first()
                #                 asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                #                                                                  asset_info=asset_info,
                #                                                                  portfolio=portfolio_spot,
                #                                                                  amount=amount,
                #                                                                  balance=balance,
                #                                                                  quantity_price=quantity_price)
                #                 self.create_tx(asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_spot,
                #                                element=element, amount=amount, user=user)
                #             elif element['type'] in ['Transfer']:
                #                 # handle transfers between spot, futures and staking portfolio
                #                 '''spotfromstaking, stakingtospot, -- stakingfromspot, spottostaking, -- spottofutures, spotfromfutures'''
                #                 if element['subtype'] in ['spottostaking', 'spotfromstaking', 'spottofutures', 'spotfromfutures']:
                #                     asset_owned = AssetOwned.objects.filter(asset=asset_info,
                #                                                             portfolio=portfolio_spot).first()
                #                     asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                #                                                                      asset_info=asset_info,
                #                                                                      portfolio=portfolio_spot,
                #                                                                      amount=amount,
                #                                                                      balance=balance,
                #                                                                      quantity_price=quantity_price)
                #                     self.create_tx(asset_info=asset_info, asset_owned=asset_owned, user=user,
                #                                    portfolio=portfolio_spot, element=element, amount=amount)
                #                 elif element['subtype'] in ['stakingfromspot', 'stakingtospot']:
                #                     asset_owned = AssetOwned.objects.filter(asset=asset_info, portfolio=portfolio_staking).first()
                #                     asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                #                                                                      asset_info=asset_info,
                #                                                                      portfolio=portfolio_staking,
                #                                                                      amount=amount,
                #                                                                      balance=balance,
                #                                                                      quantity_price=quantity_price)
                #                     self.create_tx(asset_info=asset_info, asset_owned=asset_owned, user=user,
                #                                    portfolio=portfolio_staking, element=element, amount=amount)
                #                 else:
                #                     not_found.append({
                #                         'txid': element["txid"],
                #                         'tx_refid': element["refid"],
                #                         'time': element["time"],
                #                         'type': element["type"],
                #                         'subtype': element["subtype"],
                #                         'asset': element["asset"],
                #                         'fee': element["fee"],
                #                         'balance': element["balance"]
                #                     })
                #                     continue
                #             elif element["type"] in ['Handel']:
                #                 asset_owned = AssetOwned.objects.filter(asset=asset_info,
                #                                                         portfolio=portfolio_spot).first()
                #
                #                 tx_exist = Transaction.objects.filter(user=user, tx_hash=element['refid']).exists()
                #                 print("existiert" if tx_exist else "nein existiert nicht")
                #
                #                 asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                #                                                                  asset_info=asset_info,
                #                                                                  portfolio=portfolio_spot,
                #                                                                  amount=amount,
                #                                                                  balance=balance,
                #                                                                  quantity_price=quantity_price,
                #                                                                  tx_exists=tx_exist)
                #                 self.create_tx(asset_info=asset_info, asset_owned=asset_owned, user=user,
                #                                element=element, amount=amount, portfolio=portfolio_spot)
                #             elif element["type"] in ['Gesendet']:
                #                 asset_owned = AssetOwned.objects.filter(asset=asset_info,
                #                                                         portfolio=portfolio_spot).first()
                #                 asset_owned = self.create_asset_update_portfolio(asset_owned=asset_owned,
                #                                                                  asset_info=asset_info,
                #                                                                  portfolio=portfolio_spot,
                #                                                                  amount=amount,
                #                                                                  balance=balance,
                #                                                                  quantity_price=quantity_price)
                #                 self.create_tx(asset_info=asset_info, asset_owned=asset_owned, user=user,
                #                                element=element, amount=amount, portfolio=portfolio_spot)
                # else:
                #     return Response({"error": "Dateiexport nicht akzeptiert."}, status=status.HTTP_400_BAD_REQUEST)
                return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TaxReportAPIView(APIView):
    """API View for handling pdf tax report creation and get blob from database for downloading."""
    authentication_classes = [TokenAuthentication]

    def generate_pdf_view(self, rewards, tax_year, from_date, to_date, reward_value, fee_reward_value,
                          trades, trade_value, fee_trade_value):
        """Generate tax report as pdf file from html template and return downloadable file"""
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date() if from_date else None
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date() if to_date else None

        # data for html template to convert into pdf
        context = {
            'tax_year': tax_year,
            'from_date': from_date_obj,
            'to_date': to_date_obj,
            # buy/sell/trade data
            'len_of_trades': len(trades),
            'trades_tx': trades,
            'trade_value': round(trade_value, 3) if trade_value > 0.0 else "0,00",
            'fee_trade_value': round(fee_trade_value, 3) if fee_trade_value > 0.0 else "0,00",
            'tax_free_trade_limit': '800,00',
            'total_trade_value': trade_value - fee_trade_value if reward_value > 600.00 else '0,00',
            # rewards data
            'len_of_rewards': len(rewards),
            'rewards_tx': rewards,
            'reward_value': round(reward_value, 3) if reward_value > 0.0 else "0,00",
            'fee_reward_value': round(fee_reward_value, 3) if fee_reward_value > 0.0 else "0,00",
            'tax_free_reward_limit': '256,00',
            'total_reward_value': reward_value - fee_reward_value if reward_value > 256.00 else '0,00',
            'img_path': Path(Path(__file__).parent / "templates/logo.png").absolute(),
        }

        html = render_to_string('tax-report-template.html', context)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

        return result, pdf

    def get(self, request, pk):
        try:
            token = request.auth
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
            if user is not None:
                tax_report = TaxReport.objects.get(id=pk, user=user)
                pdf_bytes = io.BytesIO(tax_report.report_pdf)
                return FileResponse(pdf_bytes, as_attachment=True,
                                    content_type='application/pdf', filename='tax-report.pdf')
        except TaxReport.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        token = request.auth
        token_obj = Token.objects.get(key=token)
        user = token_obj.user
        if user is not None:
            tax_year = request.data['taxYear']
            from_date = request.data['fromDate']
            to_date = request.data['toDate']

            transactions = None
            if tax_year is not None and from_date is None and to_date is None:
                # get all TX of given year
                transactions = Transaction.objects.filter(user=user, tx_date__year=tax_year).order_by('tx_date')
            if from_date is not None and to_date is not None and tax_year is None:
                # get all TX of given from-to date
                to_date_format_type = datetime.strptime(request.data['toDate'], '%Y-%m-%d').date()
                to_date_formatted = to_date_format_type + timedelta(days=1)
                transactions = Transaction.objects.filter(user=user, tx_date__range=[from_date, to_date_formatted]).order_by('tx_date')
            if transactions.count() == 0:
                return Response(data={'message': 'Zu diesem Steuerjahr wurden keine Transaktionen gefunden.'},
                                status=status.HTTP_204_NO_CONTENT)

            rewards_tx = []
            trades_tx = []
            for transaction in transactions:
                if transaction.tx_type.type == "Reward":
                    rewards_tx.append({
                        'date': transaction.tx_date,
                        'asset': transaction.asset.asset.acronym.upper(),
                        'amount': transaction.tx_amount,
                        'fee': transaction.tx_fee,
                        'value': round(transaction.tx_value, 3)
                    })

                # TODO: implement logic for trades (buy, sell, trade) within 1 year
                if transaction.tx_type.type in ["Kaufen", "Verkaufen", "Gesendet", "Handel"]:
                    trades_tx.append({
                        'date': transaction.tx_date,
                        'asset': transaction.asset.asset.acronym.upper(),
                        'amount': transaction.tx_amount,
                        'fee': transaction.tx_fee,
                        'value': transaction.tx_value
                    })

            # convert into dataframe
            df_rewards = pd.DataFrame(rewards_tx)
            df_trades = pd.DataFrame(trades_tx)

            # calculate sum of 'value' and 'fee' columns
            reward_value = df_rewards['value'].sum() if len(rewards_tx) > 0 else 0.00
            fee_reward_value = df_rewards['fee'].sum() if len(rewards_tx) > 0 else 0.00
            trade_value = df_trades['value'].sum() if len(trades_tx) > 0 else 0.00
            fee_trade_value = df_trades['fee'].sum() if len(trades_tx) > 0 else 0.00

            result, pdf = self.generate_pdf_view(rewards=rewards_tx, tax_year=tax_year, from_date=from_date,
                                                 to_date=to_date, reward_value=reward_value,
                                                 fee_reward_value=fee_reward_value, trades=trades_tx,
                                                 trade_value=trade_value, fee_trade_value=fee_trade_value)

            if not pdf.err:
                # Setze den Cursor des Streams zurück an den Anfang der Datei
                result.seek(0)

                pdf_content = result.read()

                tax_report = TaxReport.objects.create(user=request.user, report_pdf=pdf_content,
                                                      income_trading=trade_value, income_staking=reward_value,
                                                      year=int(tax_year) if tax_year is not None else None,
                                                      start_date=from_date if from_date is not None else None,
                                                      end_date=to_date if to_date is not None else None)
                tax_report.save()

                result.seek(0)

                return FileResponse(result, as_attachment=True,
                                    content_type='application/pdf', status=status.HTTP_201_CREATED)
            else:
                return Response(data={"error": "Irgendetwas ist schief gelaufen. Bitte versuche es erneut."},
                                status=status.HTTP_400_BAD_REQUEST)


class ExchangeApiAPIView(APIView):
    """API View for handling adding api keys to database from exchanges and retrieving new data in interval (once a day)."""
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        token = request.auth
        token_obj = Token.objects.get(key=token)
        user = token_obj.user
        if user is not None:
            api_key = request.data['apiKey']
            api_sec = request.data['apiSec']
            exchange = request.data['exchange']

            if exchange == "Kraken":
                exchange_api = ExchangeAPIs.objects.filter(user=user, api_key=api_key, api_sec=api_sec).exists()
                if not exchange_api:
                    exchange_api = ExchangeAPIs.objects.create(
                        user=user,
                        api_key=api_key,
                        api_sec=api_sec,
                        exchange_name=exchange
                    )
                    return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
                return Response(data={'message': 'API-Schlüssel zur Börse bereits vorhanden.'}, status=status.HTTP_202_ACCEPTED)
            else:
                exchange_api = ExchangeAPIs.objects.filter(user=user, api_key=api_key).exists()
                if not exchange_api:
                    exchange_api = ExchangeAPIs.objects.create(
                        user=user,
                        api_key=api_key,
                        exchange_name=exchange
                    )
                    return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
                return Response(data={'message': 'API-Schlüssel zur Börse bereits vorhanden.'}, status=status.HTTP_202_ACCEPTED)



