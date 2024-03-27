# Author: Roberto Piazza
# Date: 27.03.2023
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from django.utils import timezone
from kryptotracker.models import AssetInfo

def get_currency_data(api_id_name: str):
    """
    Get realtime cryptocurrency data from CoinGecko API.
    :param api_id_name: Name of the cryptocurrency to get data.
    :return: Return cryptocurrency data (fullname, api_id_name, symbol, current price and image).
    """
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids={api_id_name}&order=market_cap_desc&per_page=250&page=1&sparkline=false&locale=de"
    response = requests.get(url)

    if response.status_code != 200:
        return 'Fehler beim Abrufen der Daten von der API'

    data = response.json()[0]
    context = {
        'fullname': data['name'],
        'api_id_name': data['id'],
        'acronym': data['symbol'],
        'current_price': float(data['current_price']),
        'image': data['image']
    }
    return context


def get_historical_price_at_time(crypto_symbol: str, tx_date: str):
    """
    Get cryptocurrency price at given date and time from CryptoCompare API.
    :param crypto_symbol: Name of the cryptocurrency to get data.
    :param tx_date: Transaction date from HTML formular to get specific time price.
    :return: Return cryptocurrency price at specified date and time.
    """
    datetime_obj = datetime.strptime(tx_date, '%Y-%m-%dT%H:%M')
    timestamp = int(datetime_obj.timestamp())

    url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym={crypto_symbol}&tsyms=EUR&ts={timestamp}"
    response = requests.get(url)
    if response.status_code != 200:
        return 'Fehler beim Abrufen der Daten von der API'

    data = response.json()
    return float(data[crypto_symbol]['EUR'])


def get_historical_price_at_time_coingecko(crypto_id: str, tx_date: str):
    """
    Get cryptocurrency price at a given date and time from CoinGecko API using market_chart/range endpoint.
    :param crypto_id: ID of the cryptocurrency to get data.
    :param tx_date: Transaction date and time in ISO-8601 format ('YYYY-MM-DDTHH:MM').
    :return: Return cryptocurrency price at specified date and time.
    """
    # convert date into unix-timestamp
    datetime_obj = datetime.strptime(tx_date, '%Y-%m-%dT%H:%M')
    timestamp = int(datetime_obj.timestamp())

    # Festlegen des Start- und Endzeitstempels für die Anfrage
    start_timestamp = timestamp - 300  # 5 Minuten vor dem Zielzeitpunkt
    end_timestamp = timestamp + 300  # 5 Minuten nach dem Zielzeitpunkt

    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id.lower()}/market_chart/range?vs_currency=eur&from={start_timestamp}&to={end_timestamp}"

    response = requests.get(url)
    if response.status_code != 200:
        return 'Fehler beim Abrufen der Daten von der API'

    data = response.json()

    # Analyse und Extraktion des spezifischen Preises
    prices = data['prices']

    # Beispiel: Rückgabe des ersten Preises im Bereich
    return prices[0][1] if prices else 'Fehler - Keine Daten verfügbar'


def convert_crypto_amount(base_crypto: str, target_crypto: str, amount: float):
    """
    Convert a specified amount of one cryptocurrency to its equivalent in another cryptocurrency.
    :param base_crypto: Symbol of the cryptocurrency to convert from (e.g. 'BTC').
    :param target_crypto: Symbol of the cryptocurrency to convert to (e.g. 'ETH').
    :param amount: Amount of the base cryptocurrency.
    :return: Equivalent amount in the target cryptocurrency.
    """
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={base_crypto}&vs_currencies={target_crypto}'

    response = requests.get(url)
    if response.status_code != 200:
        return 'Fehler beim Abrufen der Daten von der API'

    data = response.json()
    price = data.get(base_crypto, {}).get(target_crypto)
    if price is None:
        return 'Fehler - Umrechnungskurs nicht verfügbar'

    return float(amount * price)


def get_crypto_data_from_coinmarketcap(crypto_name: str):
    """
    Get cryptocurrency data from web scraping coinmarketcap
    :param crypto_name: Name of the cryptocurrency to get data (symbol, name, price and image).
    :return: Dictionary with current cryptocurrency data (symbol, name, price and image).
    """
    url = f'https://coinmarketcap.com/de/currencies/{crypto_name}/'
    response = requests.get(url)

    if response.status_code != 200:
        return 'Fehler beim Abrufen der Webseite'

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract current cryptocurrency price and format into float
    price_selector = '.sc-f70bb44c-0.jxpCgO.base-text'
    price_element = soup.select_one(price_selector)
    if not price_element:
        return 'Fehler - Preiselement nicht gefunden'

    price_text = price_element.text.strip().replace('€', '').replace(',', '')
    try:
        # removal of spaces and commas and conversion to a number
        price = float(price_text.replace(',', ''))
    except ValueError:
        return 'Fehler - Konnte den Preis nicht in eine Zahl konvertieren'

    # Extract Image-URL
    image_selector = '[data-role="coin-logo"] img'
    image_element = soup.select_one(image_selector)
    image_src = image_element[
        'src'] if image_element and 'src' in image_element.attrs else 'Bild-Element nicht gefunden'

    # Extract Name
    name_selector = '[data-role="coin-name"]'
    name_element = soup.select_one(name_selector)
    name = name_element.get_text(strip=True) if name_element else 'Name-Element nicht gefunden'

    # Extract Symbol
    symbol_selector = '[data-role="coin-symbol"]'
    symbol_element = soup.select_one(symbol_selector)
    symbol = symbol_element.text.strip() if symbol_element else 'Symbol-Element nicht gefunden'

    return {
        'current_price': price,
        'image': image_src,
        'name': name.split('-')[0].strip(),
        'symbol': symbol
    }


def update_asset_info(asset_info: AssetInfo):
    """Update asset info image and current price. If CoinGecko fails use webscraping and get data from coinmarkecap"""
    if asset_info.api_id_name == 'euro':
        return

    current_time = timezone.now()
    time_delta = timedelta(minutes=30)
    if current_time - asset_info.updated_at < time_delta and asset_info.current_price != 0.0:
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
