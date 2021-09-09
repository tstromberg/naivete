# main is an extremely naive bot
import logging
import argparse
import os

import robin_stocks.robinhood as rh

import algo
import find
import folio
import transact


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", help="dry-run mode", action="store_true", default=True)
    parser.add_argument("--simulate-years", help="simulation mode - how many years to simulate", type=int, default=0)
    
    args = parser.parse_args()
    if args.dry_run:
        logging.info("dry-run enabled")
    else:
        logging.warning("dry-run disabled: will actually buy things.")

    ruser = os.environ["RH_USER"]
    rpass = os.environ["RH_PASS"]

    logging.info("Logging in as %s ... ", ruser)
    rh.login(ruser,rpass)
    profile = rh.build_user_profile()
    watchlist = folio.watchlist_symbols()
    logging.info("watchlist: %s", watchlist)

    portfolio = folio.portfolio_symbols()
    logging.info("portfolio: %s", portfolio)

    holdings = folio.modified_holdings()

    sells = find.sells(portfolio)
    for sym in sells:
        transact.sell(sym, holdings, dry_run=args.dry_run)

    buys = find.buys(watchlist, portfolio)
    if len(buys) > 0 and args.dry_run:
        transact.buy(buys, profile, holdings, dry_run=args.dry_run)
    
main()
