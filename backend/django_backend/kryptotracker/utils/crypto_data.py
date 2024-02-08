# Author: Roberto Piazza
# Date: 20.01.2023

from pycoingecko import CoinGeckoAPI
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup


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


# # Beispielaufruf der Funktion
# print(get_historical_price_at_time_coingecko('ethereum', '2024-01-15T12:00'))
#

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


# Beispielaufruf: Konvertiere 1.5 Bitcoin (BTC) in Ethereum (ETH)
# converted_amount = convert_crypto_amount('litecoin', 'xmr', 10)
# print(converted_amount)


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

# # Beispielaufruf
# price = get_crypto_data_from_coinmarketcap('kava')
# print(price)
