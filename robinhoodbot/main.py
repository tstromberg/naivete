# main is an extremely naive bot
import logging
import argparse
import os

import robin_stocks.robinhood

import algo
import find
import folio
import transact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", help="dry-run mode", action="store_true", default=True)
    args = parser.parse_args()
    if args.verbosity:
        print("dry-run enabled")

    ruser = os.environ("RH_USER")
    rpass = os.environ("RH_PASS")

    login = robinhood.login(ruser,rpass)
    profile = robinhood.build_user_profile()
    watchlist = folio.watchlist_symbols()
    portfolio = folio.portfolio_symbols()
    holdings = folio.modified_holdings()

    sells = find.sells(portfolio)
    for sym in sells:
        transact.sell(sym, holdings, dry_run=args.dry_run)

    buys = find.buys(watchlist, portfolio)
    if args.dry_run:
        transact.buy(buys, profile, holdings, dry_run=args.dry_run)
    
main()
