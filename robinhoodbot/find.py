import logging
import typing
import algo

def sells(portfolio: str) -> typing.List[str]:
    logging.info("Scanning portfolio for sell opportunities ...")
    sells = set()

    for symbol in portfolio:
        logging.info("symbol: %s", symbol)

        if algo.golden_cross(symbol, n1=50, n2=200, days=30, direction="below") == -1:
            logging.info("%s had a golden crossing (below)!", symbol)
            set.add(symbol)

        if algo.lowish(symbol):
            logging.info("%s is lowish", symbol)
            set.add(symbol)

    return sells

def buys(watchlist: typing.List[str], portfolio: typing.List[str]) -> typing.List[str]: 
    logging.info("Scanning portfolio for buy opportunities ...")
    buys = set()

    for symbol in watchlist:
        if symbol in portfolio:
            continue
        
        cross = algo.golden_cross(symbol, n1=50, n2=200, days=10, direction="above")
        if cross != 1:
            continue
        
        logging.info("%s had a golden crossing (above)!", symbol)
        buys.add(symbol)

    return buys