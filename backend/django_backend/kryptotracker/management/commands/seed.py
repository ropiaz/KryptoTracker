# Author: Roberto Piazza
# Date: 12.01.2023

import json
import requests
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from kryptotracker.models import *
from kryptotracker.utils import *
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

    def load_coins_from_file(self):
        """import all assets listed on coingecko api from download json-file from 06.01.2024"""
        path = Path(__file__).parent.absolute()
        file_path = path / 'coingecko_coins_list.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            for entry in data:
                coin_id = entry['id']
                symbol = entry['symbol']
                name = entry['name']
                print(f"ID: {coin_id}, Symbol: {symbol}, Name: {name}\n")
                AssetInfo.objects.create(
                    fullname=entry['name'],
                    api_id_name=entry['id'],
                    acronym=entry['symbol'],
                    current_price=0.0,
                    image=entry['image']
                )

    def get_crypto_data(self, asset_id, *kwargs):
        if len(kwargs[0]) == 0:
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids={asset_id}&order=market_cap_desc&per_page=250&page=1&sparkline=false&locale=de"
        else:
            asset_names = [name for name in kwargs[0]]
            asset_names_str = "%2C%20".join(asset_names)
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids={asset_id}%2C%20{asset_names_str}&order=market_cap_desc&per_page=250&page=1&sparkline=false&locale=de"

        response = requests.get(url)
        data = response.json()
        return data

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
            name='Kraken',
        )

        portfolio2 = Portfolio.objects.create(
            user=user,
            portfolio_type=portfolio_type_spot,
            name='Kraken',
        )

        euro_asset = AssetInfo.objects.create(
            fullname='Euro',
            api_id_name='euro',
            acronym='eur',
            current_price=1.0,
            image='https://upload.wikimedia.org/wikipedia/commons/5/5c/Euro_symbol_black.svg'
        )

        # create asset infos coinmarketcap api export => the first 2000 currencies
        self.load_coins_from_file()

        asset1 = AssetInfo.objects.get(pk=random.randint(1, 2495))
        asset2 = AssetInfo.objects.get(pk=random.randint(1, 2495))
        asset3 = AssetInfo.objects.get(pk=random.randint(1, 2495))
        asset4 = AssetInfo.objects.get(pk=random.randint(1, 2495))

        # TODO: use function from utils
        data = self.get_crypto_data(asset1.api_id_name, [asset2.api_id_name, asset3.api_id_name, asset4.api_id_name])
        i = 0
        for asset in data:
            image = asset['image']
            current_price = asset['current_price']
            if i == 0:
                asset1.image = image
                asset1.current_price = float(current_price) if current_price is not None else 0.0
                asset1.save()
            if i == 1:
                asset2.image = image
                asset2.current_price = float(current_price) if current_price is not None else 0.0
                asset2.save()
            if i == 2:
                asset3.image = image
                asset3.current_price = float(current_price) if current_price is not None else 0.0
                asset3.save()
            if i == 3:
                asset4.image = image
                asset4.current_price = float(current_price) if current_price is not None else 0.0
                asset4.save()
            i += 1

        # create dummy assets and assign to portfolio
        random_owned = random.uniform(1.0, 100.0)
        asset_info = AssetOwned.objects.create(
            portfolio=portfolio,
            asset=asset1,
            quantity_owned=random_owned,
            quantity_price=asset1.current_price * random_owned,
        )
        portfolio.balance += asset_info.quantity_price
        portfolio.save()

        random_owned = random.uniform(1.0, 100.0)
        asset_info2 = AssetOwned.objects.create(
            portfolio=portfolio2,
            asset=asset2,
            quantity_owned=random_owned,
            quantity_price=asset2.current_price * random_owned,
        )
        portfolio2.balance += asset_info2.quantity_price
        portfolio2.save()

        random_owned = random.uniform(1.0, 100.0)
        asset_info3 = AssetOwned.objects.create(
            portfolio=portfolio2,
            asset=asset3,
            quantity_owned=random_owned,
            quantity_price=asset3.current_price * random_owned,
        )
        portfolio2.balance += asset_info3.quantity_price
        portfolio2.save()

        random_owned = random.uniform(1.0, 100.0)
        asset_info4 = AssetOwned.objects.create(
            portfolio=portfolio,
            asset=asset4,
            quantity_owned=random_owned,
            quantity_price=asset4.current_price * random_owned,
        )
        portfolio.balance += asset_info4.quantity_price
        portfolio.save()

        assets = [asset_info, asset_info2, asset_info3, asset_info4]

        # create dummy transaction types
        staking_type = TransactionType.objects.create(type='Staking-Reward')
        buy_type = TransactionType.objects.create(type='Kaufen')
        sell_type = TransactionType.objects.create(type='Verkaufen')
        trade_type = TransactionType.objects.create(type='Handel')
        sent_type = TransactionType.objects.create(type='Gesendet')
        deposit_type = TransactionType.objects.create(type='Einzahlung')
        withdraw_type = TransactionType.objects.create(type='Auszahlung')
        t_types = [staking_type, buy_type, sell_type, sent_type, trade_type, deposit_type, withdraw_type]

        # create dummy transactions
        for _ in range(15):
            comment = Comment.objects.create(text=f'Das ist Dummy-Kommentar {_}.')  # create dummy comment
            random_tx_date = faker.date_time_between(start_date='-5y', end_date='now', tzinfo=pytz.UTC)
            Transaction.objects.create(
                user=user,
                asset=assets[random.randint(0, 3)],
                tx_type=t_types[random.randint(0, 4)],
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
