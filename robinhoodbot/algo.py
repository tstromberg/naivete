import logging
import argparse

import robin_stocks.robinhood as rh
import pandas
import numpy
import ta

import folio

def golden_cross(sym: str, n1: int, n2: int, days: int, direction: str) -> bool:
    """Determine if a golden/death cross has occured for a specified stock in the last X trading days

    Args:
        sym(str): Symbol of the stock we're querying
        n1(int): Specifies the short-term indicator as an X-day moving average.
        n2(int): Specifies the long-term indicator as an X-day moving average.
                 (n1 should be smaller than n2 to produce meaningful results, e.g n1=50, n2=200)
        days(int): Specifies the maximum number of days that the cross can occur by
        direction(str): "above" if we are searching for an upwards cross, "below" if we are searching for a downwaords cross. Optional, used for printing purposes

    Returns:
        1 if the short-term indicator crosses above the long-term one
        0 if there is no cross between the indicators
        -1 if the short-term indicator crosses below the long-term one
        False if direction == "above" and five_year_rise(sym) returns False, meaning that we're considering whether to
            buy the stock but it hasn't risen overall in the last five years, suggesting it contains fundamental issues
    """
    if(direction == "above" and not five_year_rise(sym)):
        return False
    
    history = rh.get_stock_historicals(sym,interval="day",span="year",bounds="regular")

    #Couldn't get pricing data
    if(history is None or None in history):
        return False
    
    closingPrices = []
    dates = []
    for item in history:
        closingPrices.append(float(item['close_price']))
        dates.append(item['begins_at'])
    price = pandas.Series(closingPrices)
    dates = pandas.Series(dates)
    dates = pandas.to_datetime(dates)
    sma1 = ta.volatility.bollinger_mavg(price, int(n1), False)
    sma2 = ta.volatility.bollinger_mavg(price, int(n2), False)
    series = [price.rename("Price"), sma1.rename("Indicator1"), sma2.rename("Indicator2"), dates.rename("Dates")]
    df = pandas.concat(series, axis=1)
    cross = last_crossing(df, days, symbol=sym, direction=direction)
    
    return cross


def lowish(sym: str) -> bool:
    """Is the stock low?"""
    history = rh.get_stock_historicals(sym,interval="day",span="year",bounds="regular")
    current = float(rh.get_latest_price(sym, priceType="bid_price")[0])
    logging.info("%s price is %s", sym, current)

    lowest = 2**32.0
    highest = -1.0

    for h in history:
        low = float(h['low_price'])
        if low == 0.0:
            logging.info("%s bad data: low=0.0: %s", sym, h)
            continue

        if low < lowest:
            lowest = low

        high = float(h['high_price'])
        if high == 0.0:
            logging.info("%s bad data: high=0.0: %s", sym, h)
            continue

        if high > highest:
            highest = high

    if current < lowest * 1.1:
        logging.info("%s buy suggest: %s is near %s", sym, current, lowest)

    if current > highest * 0.95:
        logging.info("%s sell suggest: %s is near %s", sym, current, highest)


def five_year_rise(sym: str) -> bool:
    """Figure out if a stock has risen or been created within the last five years.

    Args:
        sym(str): Symbol of the stock we're querying

    Returns:
        True if the stock's current price is higher than it was five years ago, or the stock IPO'd within the last five years
        False otherwise
    """
    instrument = rh.get_instruments_by_symbols(sym)
    if(instrument is None or len(instrument) == 0):
        return True
    list_date = instrument[0].get("list_date")
    if ((pandas.Timestamp("now") - pandas.to_datetime(list_date)) < pandas.Timedelta("5 Y")):
        return True
    fiveyear =  folio.historicals(sym, "day", "5year", "regular")
    if (fiveyear is None or None in fiveyear):
        return True
    closingPrices = []
    for item in fiveyear:
        closingPrices.append(float(item['close_price']))
    recent_price = closingPrices[len(closingPrices) - 1]
    oldest_price = closingPrices[0]
    return (recent_price > oldest_price)

def last_crossing(df, days, symbol="", direction=""):
    """Searches for a crossing between two indicators for a given stock

    Args:
        df(pandas.core.frame.DataFrame): Pandas dataframe with columns containing the stock's prices, both indicators, and the dates
        days(int): Specifies the maximum number of days that the cross can occur by
        symbol(str): Symbol of the stock we're querying. Optional, used for printing purposes
        direction(str): "above" if we are searching for an upwards cross, "below" if we are searching for a downwaords cross. Optional, used for printing purposes

    Returns:
        1 if the short-term indicator crosses above the long-term one
        0 if there is no cross between the indicators
        -1 if the short-term indicator crosses below the long-term one
    """
    prices = df.loc[:,"Price"]
    shortTerm = df.loc[:,"Indicator1"]
    LongTerm = df.loc[:,"Indicator2"]
    dates = df.loc[:,"Dates"]
    lastIndex = prices.size - 1
    index = lastIndex
    found = index
    recentDiff = (shortTerm.at[index] - LongTerm.at[index]) >= 0
    if((direction == "above" and not recentDiff) or (direction == "below" and recentDiff)):
        return 0
    index -= 1
    while(index >= 0 and found == lastIndex and not numpy.isnan(shortTerm.at[index]) and not numpy.isnan(LongTerm.at[index]) \
                        and ((pandas.Timestamp("now", tz='UTC') - dates.at[index]) <= pandas.Timedelta(str(days) + " days"))):
        if(recentDiff):
            if((shortTerm.at[index] - LongTerm.at[index]) < 0):
                found = index
        else:
            if((shortTerm.at[index] - LongTerm.at[index]) > 0):
                found = index
        index -= 1
    if(found != lastIndex):
        if((direction == "above" and recentDiff) or (direction == "below" and not recentDiff)):
            print(symbol + ": Short SMA crossed" + (" ABOVE " if recentDiff else " BELOW ") + "Long SMA at " + str(dates.at[found]) \
                +", which was " + str(pandas.Timestamp("now", tz='UTC') - dates.at[found]) + " ago", ", price at cross: " + str(prices.at[found]) \
                + ", current price: " + str(prices.at[lastIndex]))
        return (1 if recentDiff else -1)
    else:
        return 0
