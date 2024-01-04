# Author: Roberto Piazza
# Date: 04.01.2023

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from kryptotracker.models import *
from pycoingecko import CoinGeckoAPI
from faker import Faker
import pandas as pd
import random
import pytz

class Command(BaseCommand):
    help = 'Seeds the database with dummy data'

    def fetch_crypto_coins(self):
        """Get the first 100 crypto currency data from CoinGecko API and return processed dataframe"""
        cg = CoinGeckoAPI()
        parameters = {
            'vs_currency': 'eur',
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1,
            'sparkline': False,
            'locale': 'en'
        }
        coin_market_data = cg.get_coins_markets(**parameters)
        df = pd.DataFrame(coin_market_data)
        df = df.drop(['total_volume', 'market_cap', 'circulating_supply', 'total_supply', 'max_supply', 'high_24h',
                      'low_24h', 'price_change_24h', 'price_change_percentage_24h', 'market_cap_change_24h', 'ath_date',
                      'market_cap_change_percentage_24h', 'ath_change_percentage', 'atl_change_percentage', 'atl_date',
                      'fully_diluted_valuation', 'roi'], axis=1)
        return df

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        faker = Faker()

        # create dummy user
        pw = make_password("Test123")
        user = User.objects.create(username='Testuser', password=pw, email='test@test.de')

        # create dummy portfolio types
        portfolio_type_staking = PortfolioType.objects.create(type='Staking')
        portfolio_type_spot = PortfolioType.objects.create(type='Spot')

        # create dummy portfolios
        portfolio = Portfolio.objects.create(
            user=user,
            portfolio_type=portfolio_type_staking,
            name='Spot',
        )

        portfolio2 = Portfolio.objects.create(
            user=user,
            portfolio_type=portfolio_type_spot,
            name='Staking',
        )

        # fetch and create dummy assets from coingecko api
        crypto_data = self.fetch_crypto_coins()
        api_assets = []
        for index, row in crypto_data.iterrows():
            api_assets.append(
                AssetInfo.objects.create(
                    fullname=row['name'],
                    api_id_name=row['id'],
                    acronym=row['symbol'],
                    current_price=float(row['current_price']),
                    image=row['image']
                )
            )

        # create dummy assets and assign to portfolio
        random_asset = api_assets[random.randint(0, len(api_assets) - 1)]
        random_owned = random.uniform(1.0, 100.0)
        asset = AssetInfo.objects.get(pk=random_asset.id)
        asset_info = AssetOwned.objects.create(
            portfolio=portfolio,
            asset=random_asset,
            quantity_owned=random_owned,
            quantity_price=asset.current_price * random_owned,
        )
        portfolio.balance += asset_info.quantity_price
        portfolio.save()

        random_asset = api_assets[random.randint(0, len(api_assets) - 1)]
        random_owned = random.uniform(1.0, 100.0)
        asset = AssetInfo.objects.get(pk=random_asset.id)
        asset_info2 = AssetOwned.objects.create(
            portfolio=portfolio2,
            asset=random_asset,
            quantity_owned=random_owned,
            quantity_price=asset.current_price * random_owned,
        )
        portfolio2.balance += asset_info2.quantity_price
        portfolio2.save()

        random_asset = api_assets[random.randint(0, len(api_assets) - 1)]
        random_owned = random.uniform(1.0, 100.0)
        asset = AssetInfo.objects.get(pk=random_asset.id)
        asset_info3 = AssetOwned.objects.create(
            portfolio=portfolio2,
            asset=random_asset,
            quantity_owned=random_owned,
            quantity_price=asset.current_price * random_owned,
        )
        portfolio2.balance += asset_info3.quantity_price
        portfolio2.save()

        random_asset = api_assets[random.randint(0, len(api_assets) - 1)]
        random_owned = random.uniform(1.0, 100.0)
        asset = AssetInfo.objects.get(pk=random_asset.id)
        asset_info4 = AssetOwned.objects.create(
            portfolio=portfolio,
            asset=random_asset,
            quantity_owned=random_owned,
            quantity_price=asset.current_price * random_owned,
        )
        portfolio.balance += asset_info4.quantity_price
        portfolio.save()

        assets = [asset_info, asset_info2, asset_info3, asset_info4]

        # create dummy comment
        comment = Comment.objects.create(text='Das ist ein Dummy-Kommentar.')

        # create dummy transaction types
        staking_type = TransactionType.objects.create(type='Staking-Reward')
        buy_type = TransactionType.objects.create(type='Einzahlung')
        sent_type = TransactionType.objects.create(type='Gesendet')
        trade_type = TransactionType.objects.create(type='Handel')
        t_types = [staking_type, buy_type, sent_type, trade_type]

        # create dummy transactions
        for _ in range(10):
            random_tx_date = faker.date_time_between(start_date='-5y', end_date='now', tzinfo=pytz.UTC)
            Transaction.objects.create(
                user=user,
                asset=assets[random.randint(0, 3)],
                tx_type=t_types[random.randint(0, 3)],
                tx_comment=comment,
                tx_hash=f'hash{random.randint(1, 100)}',
                tx_sender_address=f'sender{random.randint(1, 100)}',
                tx_recipient_address=f'recipient{random.randint(1, 100)}',
                tx_amount=random.uniform(100.0, 1000.0),
                tx_value=random.uniform(100.0, 1000.0),
                tx_fee=random.uniform(1.0, 10.0),
                tx_date=random_tx_date
            )

        self.stdout.write(self.style.SUCCESS('Data successfully created!'))
