import logging
import typing

import robin_stocks.robinhood

def sell(symbol: str, holdings, dry_run: bool):
    """ Place an order to sell all holdings of a stock.

    Args:
        symbol(str): Symbol of the stock we want to sell
        holdings_data(dict): dict obtained from get_modified_holdings() method
    """
    shares_owned = int(float(holdings[symbol].get("quantity")))
    logging.info("####### Selling " + str(shares_owned) + " shares of " + symbol + " #######")
    if not dry_run:
        robinhood.order_sell_market(symbol, shares_owned)

def buy(syms: typing.List[str], profile, holdings, dry_run: bool):
    """Buy holdings of stock, matching average holdings in the rest of your portfolio (magic?)."""
    cash = float(profile.get('cash'))
    portfolio_value = float(profile.get('equity')) - cash
    ideal_position_size = (safe_division(portfolio_value, len(holdings))+cash/len(syms))/(2 * len(syms))
    prices = robinhood.get_latest_price(syms)

    for i in range(0, len(syms)):
        stock_price = float(prices[i])
        if(ideal_position_size < stock_price < ideal_position_size*1.5):
            num_shares = int(ideal_position_size*1.5/stock_price)
        elif (stock_price < ideal_position_size):
            num_shares = int(ideal_position_size/stock_price)
        else:
            logging.warning("####### Tried buying shares of " + syms[i] + ", but not enough buying power to do so#######")
            break

        logging.info("####### Buying " + str(num_shares) + " shares of " + syms[i] + " #######")
        if not dry_run:
            robinhood.order_buy_market(syms[i], num_shares)

def safe_division(n, d):
    return n / d if d else 0

