import logging
import argparse

import robin_stocks.robinhood as rh
import numpy
import pandas

def historicals(sym: str, interval: str, span: str, bounds: str):
    """Return historical information about a stock."""
    return rh.get_stock_historicals(sym,interval=interval,span=span,bounds=bounds)

def watchlist_symbols():
    """Return the symbols in your watchlists."""
    my_list_names = set()
    symbols = []
    
    watchlistInfo = rh.get_all_watchlists()
    for list in watchlistInfo['results']:
        listName = list['display_name']
        my_list_names.add(listName)

    for listName in my_list_names:
        list = rh.get_watchlist_by_name(name=listName)
        for item in list['results']:
            symbol = item['symbol']
            symbols.append(symbol)

    return symbols

def portfolio_symbols():
    """
    Returns: the symbol for each stock in your portfolio as a list of strings
    """
    symbols = []
    holdings_data = rh.get_open_stock_positions()
    for item in holdings_data:
        if not item:
            continue
        instrument_data = rh.get_instrument_by_url(item.get('instrument'))
        symbol = instrument_data['symbol']
        symbols.append(symbol)
    return symbols

def position_creation_date(symbol, holdings_data):
    """Returns the time at which we bought a certain stock in our portfolio

    Args:
        symbol(str): Symbol of the stock that we are trying to figure out when it was bought
        holdings_data(dict): dict returned by rh.open_stock_positions()

    Returns:
        A string containing the date and time the stock was bought, or "Not found" otherwise
    """
    instrument = rh.get_instruments_by_symbols(symbol)
    url = instrument[0].get('url')
    for dict in holdings_data:
        if(dict.get('instrument') == url):
            return dict.get('created_at')

    # wtf?
    return "Not found"

def modified_holdings():
    """ Retrieves the same dictionary as rh.build_holdings, but includes data about
        when the stock was purchased, which is useful for the read_trade_history() method
        in tradingstats.py

    Returns:
        the same dict from rh.build_holdings, but with an extra key-value pair for each
        position you have, which is 'bought_at': (the time the stock was purchased)
    """
    holdings = rh.build_holdings()
    holdings_data = rh.get_open_stock_positions()
    for symbol, _ in holdings.items():
        bought_at = position_creation_date(symbol, holdings_data)
        bought_at = str(pandas.to_datetime(bought_at))
        holdings[symbol].update({'bought_at': bought_at})
    return holdings


