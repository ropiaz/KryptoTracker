# Author: Roberto Piazza
# Date: 06.04.2023
import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from django.utils import timezone
from kryptotracker.models import AssetInfo
import logging

logger = logging.getLogger(__name__)


def get_currency_data(api_id_name: str):
    """
    Get realtime cryptocurrency data from CoinGecko API.
    :param api_id_name: Name of the cryptocurrency to get data.
    :return: Return cryptocurrency data (fullname, api_id_name, symbol, current price and image).
    """
    # url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids={api_id_name}&order=market_cap_desc&per_page=250&page=1&sparkline=false&locale=de"
    # response = requests.get(url)
    #
    # if response.status_code != 200:
    #     return 'Fehler beim Abrufen der Daten von der API'
    #
    # data = response.json()[0]
    # context = {
    #     'fullname': data['name'],
    #     'api_id_name': data['id'],
    #     'acronym': data['symbol'],
    #     'current_price': float(data['current_price']),
    #     'image': data['image']
    # }
    # return context

    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids={api_id_name}&order=market_cap_desc&per_page=250&page=1&sparkline=false&locale=de"
    try:
        response = requests.get(url)
        response.raise_for_status()  # throw exception if statuscode != 2xx
        data = response.json()[0]
        if data:
            return {
                'fullname': data['name'],
                'api_id_name': data['id'],
                'acronym': data['symbol'],
                'current_price': float(data['current_price']),
                'image': data['image']
            }
        else:
            raise Exception("API data fetch failed")
    except Exception as e:
        logger.error(f"Error retrieving data from the CoinGecko API: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error with request CoinGecko API: {e}")
        return None


def get_historical_price_at_time(crypto_symbol: str, tx_date: str):
    """
    Get cryptocurrency price at given date and time from CryptoCompare API.
    :param crypto_symbol: Name of the cryptocurrency to get data.
    :param tx_date: Transaction date from HTML formular to get specific time price.
    :return: Return cryptocurrency price at specified date and time.
    """
    # datetime_obj = datetime.strptime(tx_date, '%Y-%m-%dT%H:%M')
    # timestamp = int(datetime_obj.timestamp())
    #
    # url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym={crypto_symbol}&tsyms=EUR&ts={timestamp}"
    # response = requests.get(url)
    # if response.status_code != 200:
    #     return 'Error retrieving data from the API'
    #
    # data = response.json()
    # return float(data[crypto_symbol]['EUR'])
    datetime_obj = datetime.strptime(tx_date, '%Y-%m-%dT%H:%M')
    timestamp = int(datetime_obj.timestamp())
    url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym={crypto_symbol}&tsyms=EUR&ts={timestamp}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data[crypto_symbol]['EUR']:
            return float(data[crypto_symbol]['EUR'])
        else:
            raise Exception(f"Could not get price for {crypto_symbol}")
    except Exception as e:
        logger.error(f"Error retrieving data from the API: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error retrieving data from the API: {e}")
        return None


def get_historical_price_at_time_coingecko(crypto_id: str, tx_date: str):
    """
    Get cryptocurrency price at a given date and time from CoinGecko API using market_chart/range endpoint.
    :param crypto_id: ID of the cryptocurrency to get data.
    :param tx_date: Transaction date and time in ISO-8601 format ('YYYY-MM-DDTHH:MM').
    :return: Return cryptocurrency price at specified date and time.
    """
    # response = requests.get(url)
    # if response.status_code != 200:
    #     return 'Fehler beim Abrufen der Daten von der API'
    # data = response.json()
    # # Analyse und Extraktion des spezifischen Preises
    # prices = data['prices']
    # # Beispiel: Rückgabe des ersten Preises im Bereich
    # return prices[0][1] if prices else 'Fehler - Keine Daten verfügbar'

    # convert date into unix-timestamp
    datetime_obj = datetime.strptime(tx_date, '%Y-%m-%dT%H:%M')
    timestamp = int(datetime_obj.timestamp())
    # choose start- and end timestamp for api query
    start_timestamp = timestamp - 300  # 5 mins target time
    end_timestamp = timestamp + 300  # 5 mins after target time
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id.lower()}/market_chart/range?vs_currency=eur&from={start_timestamp}&to={end_timestamp}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = data['prices']
        if prices:
            return prices[0][1]
        else:
            raise Exception("No price data found")
    except Exception as e:
        logger.error(f"Error retrieving data from the API: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error retrieving data from the API: {e}")
        return None


def convert_crypto_amount(base_crypto: str, target_crypto: str, amount: float):
    """
    Convert a specified amount of one cryptocurrency to its equivalent in another cryptocurrency.
    :param base_crypto: Symbol of the cryptocurrency to convert from (e.g. 'BTC').
    :param target_crypto: Symbol of the cryptocurrency to convert to (e.g. 'ETH').
    :param amount: Amount of the base cryptocurrency.
    :return: Equivalent amount in the target cryptocurrency.
    """
    # response = requests.get(url)
    # if response.status_code != 200:
    #     return 'Fehler beim Abrufen der Daten von der API'
    #
    # data = response.json()
    # price = data.get(base_crypto, {}).get(target_crypto)
    # if price is None:
    #     return 'Fehler - Umrechnungskurs nicht verfügbar'
    #
    # return float(amount * price)
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={base_crypto}&vs_currencies={target_crypto}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price = data.get(base_crypto, {}).get(target_crypto)
        if price is not None:
            return float(amount * price)
        else:
            raise Exception("Exchange rate not available")
    except Exception as e:
        logger.error(f"Error retrieving data from the API: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error retrieving data from the API: {e}")
        return None


def get_crypto_data_from_coinmarketcap(crypto_name: str):
    """
    Get cryptocurrency data from web scraping coinmarketcap
    :param crypto_name: Name of the cryptocurrency to get data (symbol, name, price and image).
    :return: Dictionary with current cryptocurrency data (symbol, name, price and image).
    """
    # url = f'https://coinmarketcap.com/de/currencies/{crypto_name}/'
    # response = requests.get(url)
    #
    # if response.status_code != 200:
    #     return 'Fehler beim Abrufen der Webseite'

    # soup = BeautifulSoup(response.text, 'html.parser')
    #
    # # Extract current cryptocurrency price and format into float
    # price_selector = '.sc-f70bb44c-0.jxpCgO.base-text'
    # price_element = soup.select_one(price_selector)
    # if not price_element:
    #     return 'Fehler - Preiselement nicht gefunden'
    #
    # price_text = price_element.text.strip().replace('€', '').replace(',', '')
    # try:
    #     # removal of spaces and commas and conversion to a number
    #     price = float(price_text.replace(',', ''))
    # except ValueError:
    #     return 'Fehler - Konnte den Preis nicht in eine Zahl konvertieren'
    #
    # # Extract Image-URL
    # image_selector = '[data-role="coin-logo"] img'
    # image_element = soup.select_one(image_selector)
    # image_src = image_element[
    #     'src'] if image_element and 'src' in image_element.attrs else 'Bild-Element nicht gefunden'
    #
    # # Extract Name
    # name_selector = '[data-role="coin-name"]'
    # name_element = soup.select_one(name_selector)
    # name = name_element.get_text(strip=True) if name_element else 'Name-Element nicht gefunden'
    #
    # # Extract Symbol
    # symbol_selector = '[data-role="coin-symbol"]'
    # symbol_element = soup.select_one(symbol_selector)
    # symbol = symbol_element.text.strip() if symbol_element else 'Symbol-Element nicht gefunden'
    #
    # return {
    #     'current_price': price,
    #     'image': image_src,
    #     'name': name.split('-')[0].strip(),
    #     'symbol': symbol
    # }
    url = f'https://coinmarketcap.com/de/currencies/{crypto_name}/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract current cryptocurrency price and format into float
        price_selector = '.sc-f70bb44c-0.jxpCgO.base-text'
        price_element = soup.select_one(price_selector)
        if not price_element:
            raise Exception("Price element not found with webscraping")
            # return 'Fehler - Preiselement nicht gefunden'

        price_text = price_element.text.strip().replace('€', '').replace(',', '')
        try:
            # removal of spaces and commas and conversion to a number
            price = float(price_text.replace(',', ''))
        except ValueError:
            logger.error("Could not convert the price to a number after webscraping")
            return None
            # return 'Fehler - Konnte den Preis nicht in eine Zahl konvertieren'

        # Extract Image-URL
        image_selector = '[data-role="coin-logo"] img'
        image_element = soup.select_one(image_selector)
        # image_src = image_element['src'] if image_element and 'src' in image_element.attrs else 'Bild-Element nicht gefunden'
        image_src = image_element['src']

        # Extract Name
        name_selector = '[data-role="coin-name"]'
        name_element = soup.select_one(name_selector)
        # name = name_element.get_text(strip=True) if name_element else 'Name-Element nicht gefunden'
        name = name_element.get_text(strip=True)

        # Extract Symbol
        symbol_selector = '[data-role="coin-symbol"]'
        symbol_element = soup.select_one(symbol_selector)
        # symbol = symbol_element.text.strip() if symbol_element else 'Symbol-Element nicht gefunden'
        symbol = symbol_element.text.strip()

        if not all([price_element, image_element, name_element, symbol_element]):
            raise Exception("Not all data available with webscraping")
        else:
            return {
                'current_price': price,
                'image': image_src,
                'name': name.split('-')[0].strip(),
                'symbol': symbol
            }
    except Exception as e:
        logger.error(f"Error retrieving data from webscraping: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error retrieving data from webscraping: {e}")
        return None


# TODO: what if api call and webscraping fails?
def update_asset_info(asset_info: AssetInfo):
    """Update asset info image and current price. If CoinGecko fails use webscraping and get data from coinmarkecap"""
    if asset_info.api_id_name == 'euro':
        return

    current_time = timezone.now()
    time_delta = timedelta(minutes=30)
    if current_time - asset_info.updated_at < time_delta and asset_info.current_price != 0.0:
        return

    try:
        if asset_info.fullname == "EthereumPoW":
            new_data = get_crypto_data_from_coinmarketcap(crypto_name=asset_info.api_id_name[:-4])
            if new_data is not None:
                asset_info.current_price = new_data['current_price']
                asset_info.image = new_data['image']
                asset_info.save()
        else:
            new_data = get_currency_data(api_id_name=asset_info.api_id_name)
            # if 'current_price' in new_data and 'image' in new_data:
            if new_data is not None:
                asset_info.current_price = new_data['current_price']
                asset_info.image = new_data['image']
                asset_info.save()
            else:
                new_data = get_crypto_data_from_coinmarketcap(crypto_name=asset_info.api_id_name)
                if new_data is not None:
                    asset_info.current_price = new_data['current_price']
                    asset_info.image = new_data['image']
                    asset_info.save()
                else:
                    raise Exception(f"AssetInfo {asset_info.fullname} could not be updated with api request and webscraping")
    except Exception as e:
        logger.error(f"Update error: {e}")
        return None


def map_kraken_coins():
    """Return kraken asset symbols (acronym) mapped to originals in CoinGecko or CoinMarketCap"""
    return {
        'ADA.S': 'ADA',
        'ALGO.S': 'ALGO',
        'ATOM.S': 'ATOM',
        'ATOM21.S': 'ATOM',
        'DOT.S': 'DOT',
        'DOT28.S': 'DOT',
        'ETH2': 'ETH',
        'ETH2.S': 'ETH',
        # 'ETHW': 'ETH',
        'FLOW.S': 'FLOW',
        'FLOW14.S': 'FLOW',
        'FLOWH.S': 'FLOW',
        'FLR.S': 'FLR',
        'GRT.S': 'GRT',
        'GRT28.S': 'GRT',
        'KAVA.S': 'KAVA',
        'KAVA21.S': 'KAVA',
        'KSM.S': 'KSM',
        'KSM07.S': 'KSM',
        'LUNA.S': 'LUNA',
        'MATIC.S': 'MATIC',
        'MATIC04.S': 'MATIC',
        'MINA.S': 'MINA',
        'SCRT.S': 'SCRT',
        'SCRT21.S': 'SCRT',
        'SOL.S': 'SOL',
        'SOL03.S': 'SOL',
        'USDC.M': 'USDC',
        'USDT.M': 'USDT',
        'XBT.M': 'BTC',
        'TRX.S': 'TRX',
        'XBT': 'BTC',
        'XETC': 'ETC',
        'XETH': 'ETH',
        'XTZ.S': 'XTZ',
        'XLTC': 'LTC',
        'XMLN': 'MLN',
        'XREP': 'REP',
        'XXBT': 'BTC',
        'XXDG': 'XDG',
        'XXLM': 'XLM',
        'XXMR': 'XMR',
        'XXRP': 'XRP',
        'XZEC': 'ZEC',
        'ZAUD': 'AUD',
        'ZCAD': 'CAD',
        'ZEUR': 'EUR',
        'ZGBP': 'GBP',
        'ZJPY': 'JPY',
        'ZUSD': 'USD',
    }


def map_kraken_tx_types():
    """Return mapped transaction types from kraken csv export for database predefined types"""
    return {
        'trade': 'Handel',
        'deposit': 'Einzahlung',
        'withdrawal': 'Gesendet',
        'staking': 'Reward',
        'earn': 'Reward',
        'buy': 'Kaufen',
        'sell': 'Verkaufen',
        'transfer': 'Transfer'
    }


def get_coin_pairs(dataframe: pd.DataFrame):
    """Return separated coin pairs from Kraken API e.g. for XXBTZEUR is XXBT and ZEUR"""
    # pairs = set([row['pair'] for index, row in dataframe.iterrows()])
    # joined_pairs_list = ",".join(pairs)
    # url = f'https://api.kraken.com/0/public/AssetPairs?pair={joined_pairs_list}'
    # response = requests.get(url)
    # if response.status_code != 200:
    #     return 'Fehler beim Abrufen der Daten von der API'
    #
    # data = response.json()['result']
    # return data
    pairs = set([row['pair'] for index, row in dataframe.iterrows()])
    joined_pairs_list = ",".join(pairs)
    url = f'https://api.kraken.com/0/public/AssetPairs?pair={joined_pairs_list}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['result']
        if data:
            return data
        else:
            raise Exception("Asset Pairs could not be separated")
    except Exception as e:
        logger.error(f"Error retrieving data from the API: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error retrieving data from the API: {e}")
        return None
