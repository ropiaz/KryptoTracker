# Author: Roberto Piazza
# Date: 27.03.2023

import pytz
import time
import hmac
import hashlib
import base64
import requests
import urllib.parse
import pandas as pd
from datetime import datetime
from kryptotracker.models import *
from kryptotracker.utils import crypto_data
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

def get_kraken_signature(urlpath, data, secret):
    """Kraken Security"""
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_request(uri_path, data, api_key, api_sec):
    """Attaches auth headers and returns results of a POST request"""
    api_url = "https://api.kraken.com"
    headers = {
        'API-Key': api_key,
        'API-Sign': get_kraken_signature(uri_path, data, api_sec)
    }
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req


def get_kraken_balances(a_key, a_sec):
    """Return kraken balances greater than 0.00005 from kraken api"""
    nonce = str(1000 * int(1000 * time.time()))
    resp = kraken_request(uri_path='/0/private/Balance', data={"nonce": nonce}, api_key=a_key, api_sec=a_sec)
    # remove coins with < 0.00005
    balances = {coin: balance for coin, balance in resp.json()["result"].items() if float(balance) > 1e-05}
    return balances


def get_kraken_staking_data(a_key, a_sec):
    """Return staking data from kraken api"""
    nonce = str(1000 * int(1000 * time.time()))
    resp = kraken_request(uri_path='/0/private/Earn/Allocations', data={
        "nonce": nonce,
        "converted_asset": "EUR",
        "hide_zero_allocations": "true"
    }, api_key=a_key, api_sec=a_sec)
    return resp.json()['result']


def get_kraken_trade_history(a_key, a_sec):
    """Return trade history from kraken api"""
    nonce = str(1000 * int(1000 * time.time()))
    resp = kraken_request('/0/private/TradesHistory', {
        "nonce": nonce
    }, a_key, a_sec)
    return resp.json()['result']


def get_kraken_ledgers_info(a_key, a_sec, start=None):
    """Return ledgers info from kraken api"""
    nonce = str(1000 * int(1000 * time.time()))
    if start is None:
        resp = kraken_request('/0/private/Ledgers', {
            "nonce": nonce,
        }, a_key, a_sec)
    else:
        resp = kraken_request('/0/private/Ledgers', {
            "nonce": nonce,
            "start": start
        }, a_key, a_sec)
    return resp.json()['result']


# Start: ########################### Handle Spot and Staking Portfolio Update ############################
def handle_portfolio_update(user: User, balances: dict, staking_allocations: dict) -> None:
    """Update user staking and spot portfolio with current data from kraken exchange."""
    cleaned_balances = clean_map_balances(data=balances)
    extracted_staking_data = extract_staking_data(data=staking_allocations['items'])

    # get or create portfolios
    portfolio_staking, portfolio_spot = get_or_create_portfolios(user=user, staking_data=extracted_staking_data)
    # update staking portfolio
    if len(extracted_staking_data) > 0:
        update_staking_portfolio(staking_portfolio=portfolio_staking, data=extracted_staking_data)
    # update spot portfolio
    if len(cleaned_balances.keys()) > 0:
        update_spot_portfolio(spot_portfolio=portfolio_spot, data=cleaned_balances)


def clean_map_balances(data: dict) -> dict:
    """Remove staking assets from balance due to doubles with staking_allocations and map coins."""
    # remove staking assets
    cleaned_balances = {key: value for key, value in data.items() if not key.endswith('.S') and not key.endswith('.M')}
    # map coins
    coin_mapping = crypto_data.map_kraken_coins()
    mapped_balances = {coin_mapping.get(key, key): value for key, value in cleaned_balances.items()}
    return mapped_balances


def extract_staking_data(data: dict) -> list:
    """Return current staking data from staking portfolio"""
    coin_mapping = crypto_data.map_kraken_coins()

    extracted_data = []
    for item in data:
        # drop unnecessary elements
        item.pop('payout', None)
        item.pop('strategy_id', None)
        if 'unbonding' in item['amount_allocated']:
            item['amount_allocated'].pop('unbonding', None)
        if 'allocations' in item['amount_allocated']:
            item['amount_allocated'].pop('allocations', None)

        # map kraken asset names with original
        if item['native_asset'] in coin_mapping:
            item['native_asset'] = coin_mapping[item['native_asset']]

        extracted_data.append({
            'asset': item['native_asset'],
            'amount': item['amount_allocated']['total']['native'],
            'converted': item['amount_allocated']['total']['converted']
        })
    return extracted_data


def get_or_create_portfolios(user: User, staking_data: list = None, ledgers: bool = False, dataframe: pd.DataFrame = None) -> [Portfolio]:
    """Return a list of Portfolio objects (Staking- and Spot-Portfolio from User). Create one if it doesn't exist."""
    if not ledgers:
        portfolio_type_spot = PortfolioType.objects.filter(type="Spot").first()
        portfolio_type_staking = PortfolioType.objects.filter(type="Staking").first()
        portfolio_spot = Portfolio.objects.filter(user=user,
                                                  portfolio_type=portfolio_type_spot,
                                                  name="Kraken").first()
        portfolio_staking = Portfolio.objects.filter(user=user,
                                                     portfolio_type=portfolio_type_staking,
                                                     name="Kraken").first()

        if len(staking_data) > 0 and portfolio_staking is None:
            portfolio_staking = Portfolio.objects.create(user=user,
                                                         name='Kraken',
                                                         balance=0.0,
                                                         portfolio_type=portfolio_type_staking)
        if portfolio_spot is None:
            portfolio_spot = Portfolio.objects.create(user=user,
                                                      name='Kraken',
                                                      balance=0.0,
                                                      portfolio_type=portfolio_type_spot)
    else:
        portfolio_type_spot = PortfolioType.objects.filter(type="Spot").first()
        portfolio_type_staking = PortfolioType.objects.filter(type="Staking").first()

        # check if user has staking and spot portfolio with name "Kraken"
        portfolio_spot = Portfolio.objects.filter(user=user,
                                                  portfolio_type=portfolio_type_spot,
                                                  name="Kraken").first()
        portfolio_staking = Portfolio.objects.filter(user=user,
                                                     portfolio_type=portfolio_type_staking,
                                                     name="Kraken").first()

        if "Reward" in dataframe['type'].values and portfolio_staking is None:
            portfolio_staking = Portfolio.objects.create(user=user,
                                                         name='Kraken',
                                                         balance=0.0,
                                                         portfolio_type=portfolio_type_staking)
        if portfolio_spot is None:
            portfolio_spot = Portfolio.objects.create(user=user,
                                                      name='Kraken',
                                                      balance=0.0,
                                                      portfolio_type=portfolio_type_spot)
    return portfolio_staking, portfolio_spot


def update_staking_portfolio(staking_portfolio: Portfolio, data: list) -> None:
    """Update staking portfolio and their assets (amount, quantity_price) based on provided data from kraken API"""
    sum_staking = 0.0
    for staking_data in data:
        sum_staking += float(staking_data['converted'])
        asset_info = AssetInfo.objects.filter(acronym=staking_data['asset']).first()
        crypto_data.update_asset_info(asset_info=asset_info)
        if asset_info is not None:
            asset_in_staking = AssetOwned.objects.filter(asset=asset_info, portfolio=staking_portfolio).first()
            if asset_in_staking is None:
                asset_in_staking = AssetOwned.objects.create(
                    asset=asset_info,
                    portfolio=staking_portfolio,
                    quantity_owned=float(staking_data['amount']),
                    quantity_price=float(staking_data['converted'])
                )
                staking_portfolio.balance += float(staking_data['converted'])
                staking_portfolio.save()
            else:
                asset_in_staking.quantity_owned = float(staking_data['amount'])
                asset_in_staking.quantity_price = float(staking_data['converted'])
                asset_in_staking.save()
    staking_portfolio.balance = sum_staking
    staking_portfolio.save()


def update_spot_portfolio(spot_portfolio: Portfolio, data: dict) -> None:
    """Update spot portfolio and their assets (quantity_owned, quantity_price) based on provided data from kraken API"""
    sum_spot = 0
    for crpyto_symbol, amount in data.items():
        asset_info = AssetInfo.objects.filter(acronym=crpyto_symbol).first()
        if asset_info is not None:
            if asset_info.fullname == "EthereumPoW":
                data = crypto_data.get_crypto_data_from_coinmarketcap(crypto_name=asset_info.api_id_name[:-4])
                asset_info.current_price = data['current_price']
                asset_info.image = data['image']
                asset_info.save()
            else:
                crypto_data.update_asset_info(asset_info=asset_info)
            quantity_price = asset_info.current_price * float(amount)
            sum_spot += quantity_price
            asset_in_spot = AssetOwned.objects.filter(asset=asset_info, portfolio=spot_portfolio).first()
            if asset_in_spot is None and crpyto_symbol != 'KFEE':
                asset_in_spot = AssetOwned.objects.create(
                    asset=asset_info,
                    portfolio=spot_portfolio,
                    quantity_owned=float(amount),
                    quantity_price=quantity_price
                )
                spot_portfolio.balance += quantity_price
                spot_portfolio.save()
            else:
                asset_in_spot.quantity_owned = float(amount)
                asset_in_spot.quantity_price = quantity_price
                asset_in_spot.save()
    spot_portfolio.balance = sum_spot
    spot_portfolio.save()
# End: ########################### Handle Spot and Staking Portfolio Update ############################


# Start: ########################### Handle import of new transactions in ledgers ############################
# TODO: import new tx according to type
def handle_new_ledger_tx(user: User, data: dict):
    """Iterate through ledgers dictionary with new transactions and handle the import"""
    # convert timestamp into datetime from all elements 'time'
    transformed_data = {
        tx_id: {**tx_data,
                'time': datetime.fromtimestamp(tx_data['time'], tz=pytz.UTC) if 'time' in tx_data else tx_data['time']}
        for tx_id, tx_data in data.items()
    }

    # create dataframe from transformed data
    df = create_dataframe_from_ledgers_data(data=transformed_data)
    print(df)

    portfolio_staking, portfolio_spot = get_or_create_portfolios(user=user, ledgers=True, dataframe=df)

    # TODO: import tx according to tx_type
    for index, element in df.iterrows():
        print(index)
        tx_exists = Transaction.objects.filter(user=user, tx_hash=element['tx_id']).exists()
        if tx_exists:
            continue

        asset_info = AssetInfo.objects.filter(acronym=element["asset"]).first()
        if asset_info is not None:
            # amount = element['amount']
            # balance = element['balance']
            # crypto_data.update_asset_info(asset_info=asset_info)
            # quantity_price = amount * asset_info.current_price

            if element['type'] == "Reward":
                asset_owned = AssetOwned.objects.filter(asset=asset_info,
                                                        portfolio=portfolio_staking).first()
                # asset_owned = create_asset_update_portfolio(asset_owned=asset_owned,
                #                                             asset_info=asset_info,
                #                                             portfolio=portfolio_staking,
                #                                             amount=amount,
                #                                             balance=balance,
                #                                             quantity_price=quantity_price)
                create_tx(user=user, asset_info=asset_info, asset_owned=asset_owned, portfolio=portfolio_staking,
                          element=element)


def create_dataframe_from_ledgers_data(data: dict) -> pd.DataFrame:
    """Create a dataframe from ledgers dictionary, transform time column from timestamp to datetime and map asset and tx types."""
    records = []
    for key, values in data.items():
        record = values.copy()
        record['tx_id'] = key
        records.append(record)
    df = pd.DataFrame(records)

    # drop unnecessary column and convert time, asset and type fields
    df = df.drop(columns=['aclass'])
    df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%dT%H:%M')
    coin_mapping = crypto_data.map_kraken_coins()
    df['asset'] = df['asset'].map(coin_mapping).fillna(df['asset'])
    tx_type_mapping = crypto_data.map_kraken_tx_types()
    df['type'] = df['type'].map(tx_type_mapping).fillna(df['type'])
    df = df['migration' != df['subtype']]
    df = df.sort_values(by='time', ascending=True)
    return df


def create_tx(user: User, asset_info: AssetInfo, asset_owned: AssetOwned, portfolio: Portfolio, element: pd.DataFrame.items) -> None:
    tx_fee = element['fee']
    tx_date = element['time']
    asset = element['asset']
    amount = float(element['amount'])

    datetime_price = amount  # TODO: correct standard value?
    if asset != 'EUR':
        # get price on tx_date with coingecko, if error try cryotocompare api otherwise 0.0 and TODO: update later
        datetime_price = crypto_data.get_historical_price_at_time_coingecko(crypto_id=asset_info.api_id_name,
                                                                            tx_date=tx_date) if asset_info.api_id_name != "euro" else 1.0
        if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
            datetime_price = crypto_data.get_historical_price_at_time(tx_date=tx_date,
                                                                      crypto_symbol=asset) if asset_info.api_id_name != "euro" else 1.0
            if not isinstance(datetime_price, float) and datetime_price.startswith("Fehler"):
                datetime_price = 0.0

    type_tx = TransactionType.objects.get(type=element['type'])
    comment_text = f"{portfolio.name}-API-Import: {amount} {asset}"
    comment = Comment.objects.create(text=comment_text)
    Transaction.objects.create(
        user=user,
        asset=asset_owned,
        tx_type=type_tx,
        tx_comment=comment,
        tx_hash=element['tx_id'],
        tx_amount=amount,
        tx_value=datetime_price * amount if asset != 'EUR' else amount,
        tx_fee=tx_fee,
        tx_date=tx_date,
        status=False if datetime_price == 0.0 else True
    )

# End: ########################### Handle import of new transactions in ledgers ############################


class Command(BaseCommand):
    help = 'Call exchange APIs, retrieve data and store new data in database'

    def handle(self, *args, **options):
        self.stdout.write('API Request...')
        exchange_apis = ExchangeAPIs.objects.all()
        # go through each api and check for new data in their exchange
        for exchange_api in exchange_apis:
            user = exchange_api.user
            exchange_name = exchange_api.exchange_name
            api_key = exchange_api.api_key
            api_sec = exchange_api.api_sec

            # update spot and staking portfolio balances
            # portfolio_balances = get_kraken_balances(a_key=api_key, a_sec=api_sec)
            # staking_allocations = get_kraken_staking_data(a_key=api_key, a_sec=api_sec)
            # handle_portfolio_update(user=user, balances=portfolio_balances, staking_allocations=staking_allocations)


            # check if user has transactions and get the last one
            tx = Transaction.objects.filter(user=user).last()
            print(tx.tx_date)
            if tx and tx.tx_date:
                # convert datetime into timestamp and handle import of new transactions after the timestamp
                timestamp = int(tx.tx_date.timestamp())
                ledger_history = get_kraken_ledgers_info(a_key=api_key, a_sec=api_sec, start=timestamp)
                if ledger_history['count'] > 0:
                    new_data = ledger_history['ledger']
                    handle_new_ledger_tx(user=user, data=new_data)
            else:
                # retrieve all ledgers transaction and handle import
                ledger_history = get_kraken_ledgers_info(a_key=api_key, a_sec=api_sec, start=None)
                if ledger_history['count'] > 0:
                    new_data = ledger_history['ledger']
                    handle_new_ledger_tx(user=user, data=new_data)

        self.stdout.write('Finished API Import...')
