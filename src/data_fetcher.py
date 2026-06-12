import ssl
import time
import random
import json
import os
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings()

_session = requests.Session()
_session.verify = False
_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

import yfinance as yf

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def fetch_indian_stock(ticker: str, exchange: str = "NSE") -> dict:
    """
    Fetches live financial data for an Indian stock from Yahoo Finance.
    NSE stocks use .NS suffix, BSE stocks use .BO suffix.
    """
    suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
    full_ticker = f"{ticker.upper()}{suffix}"

    print(f"\nFetching live data for {full_ticker} from Yahoo Finance...")

    # Check cache first
    cache_file = f"{CACHE_DIR}/{full_ticker}_{datetime.today().date()}.json"
    if os.path.exists(cache_file):
        print("Loading from local cache...")
        with open(cache_file, "r") as f:
            return json.load(f)

    # Random delay to avoid rate limiting
    time.sleep(random.uniform(2.0, 4.0))

    def safe_get(df, keys):
        if df is None or df.empty:
            return None
        for key in keys:
            if key in df.index:
                val = df.loc[key].iloc[0]
                if val is not None and str(val) != "nan":
                    return float(val)
        return None

    try:
        stock = yf.Ticker(full_ticker, session=_session)

        info       = stock.info
        financials = stock.financials
        balance    = stock.balance_sheet

        ebit = safe_get(financials, ["EBIT", "Operating Income", "OperatingIncome"])
        interest_expense = safe_get(financials, ["Interest Expense", "InterestExpense", "Net Interest Income"])
        net_income = safe_get(financials, ["Net Income", "NetIncome", "Net Income Common Stockholders"])
        total_revenue = safe_get(financials, ["Total Revenue", "TotalRevenue", "Revenue"])
        total_assets = safe_get(balance, ["Total Assets", "TotalAssets"])
        total_equity = safe_get(balance, ["Stockholders Equity", "StockholdersEquity", "Common Stock Equity"])
        current_assets = safe_get(balance, ["Current Assets", "CurrentAssets"])
        current_liabilities = safe_get(balance, ["Current Liabilities", "CurrentLiabilities"])
        retained_earnings = safe_get(balance, ["Retained Earnings", "RetainedEarnings"])
        total_liabilities = safe_get(balance, ["Total Liabilities Net Minority Interest", "Total Liabilities"])

        market_cap    = info.get("marketCap", None)
        current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
        pe_ratio      = info.get("trailingPE", None)
        company_name  = info.get("longName", info.get("shortName", ticker))

        working_capital = None
        if current_assets is not None and current_liabilities is not None:
            working_capital = current_assets - current_liabilities

        if interest_expense is not None:
            interest_expense = abs(interest_expense)

        result = {
            "company_name"     : company_name,
            "ticker"           : full_ticker,
            "exchange"         : exchange.upper(),
            "current_price"    : current_price,
            "market_cap"       : market_cap,
            "pe_ratio"         : pe_ratio,
            "ebit"             : ebit,
            "interest_expense" : interest_expense,
            "net_income"       : net_income,
            "total_revenue"    : total_revenue,
            "total_assets"     : total_assets,
            "total_equity"     : total_equity,
            "total_liabilities": total_liabilities,
            "working_capital"  : working_capital,
            "retained_earnings": retained_earnings,
        }

        print(f"\n{'='*50}")
        print(f"  Live Data Fetched: {company_name} ({full_ticker})")
        print(f"{'='*50}")
        print(f"  Current Price : ₹{current_price:,.2f}" if current_price else "  Current Price : N/A")
        print(f"  Market Cap    : ₹{market_cap:,.0f}" if market_cap else "  Market Cap    : N/A")
        print(f"  EBIT          : ₹{ebit:,.0f}" if ebit else "  EBIT          : N/A")
        print(f"  Net Income    : ₹{net_income:,.0f}" if net_income else "  Net Income    : N/A")
        print(f"  Total Assets  : ₹{total_assets:,.0f}" if total_assets else "  Total Assets  : N/A")
        print(f"{'='*50}\n")

        # Save to cache
        with open(cache_file, "w") as f:
            json.dump(result, f, default=str)

        return result

    except Exception as e:
        print(f"Error fetching data for {full_ticker}: {e}")
        return {}