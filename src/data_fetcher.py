import ssl
import requests
import urllib3
urllib3.disable_warnings()

import yfinance as yf

# Create a session that bypasses SSL verification
_session = requests.Session()
_session.verify = False
import yfinance as yf


def fetch_indian_stock(ticker: str, exchange: str = "NSE") -> dict:
    """
    Fetches live financial data for an Indian stock from Yahoo Finance.

    Parameters:
    - ticker  : Stock symbol WITHOUT exchange suffix. E.g. "RELIANCE", "TCS", "INFY"
    - exchange: "NSE" (default) or "BSE"

    How Indian tickers work on Yahoo Finance:
    - NSE stocks use .NS suffix  → RELIANCE.NS
    - BSE stocks use .BO suffix  → RELIANCE.BO

    Returns a dictionary of key financial figures needed by the agent.
    """

    # Build the full Yahoo Finance ticker string
    suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
    full_ticker = f"{ticker.upper()}{suffix}"

    print(f"\nFetching live data for {full_ticker} from Yahoo Finance...")

    try:
        stock = yf.Ticker(full_ticker, session=_session)

        # Three data sources from yfinance:
        info         = stock.info              # Market data, company overview
        financials   = stock.financials        # Income statement (annual)
        balance      = stock.balance_sheet     # Balance sheet (annual)

        def safe_get(df, keys):
            """
            Safely extracts a value from a DataFrame.
            Tries multiple possible key names because Yahoo Finance
            uses different labels for the same metric depending on the stock.
            """
            if df is None or df.empty:
                return None
            for key in keys:
                if key in df.index:
                    val = df.loc[key].iloc[0]
                    if val is not None and str(val) != "nan":
                        return float(val)
            return None

        # --- Income Statement figures ---
        ebit = safe_get(financials, [
            "EBIT", "Operating Income", "OperatingIncome"
        ])
        interest_expense = safe_get(financials, [
            "Interest Expense", "InterestExpense",
            "Net Interest Income"
        ])
        net_income = safe_get(financials, [
            "Net Income", "NetIncome",
            "Net Income Common Stockholders"
        ])
        total_revenue = safe_get(financials, [
            "Total Revenue", "TotalRevenue", "Revenue"
        ])

        # --- Balance Sheet figures ---
        total_assets = safe_get(balance, [
            "Total Assets", "TotalAssets"
        ])
        total_equity = safe_get(balance, [
            "Stockholders Equity", "StockholdersEquity",
            "Total Equity Gross Minority Interest",
            "Common Stock Equity"
        ])
        current_assets = safe_get(balance, [
            "Current Assets", "CurrentAssets"
        ])
        current_liabilities = safe_get(balance, [
            "Current Liabilities", "CurrentLiabilities"
        ])
        retained_earnings = safe_get(balance, [
            "Retained Earnings", "RetainedEarnings",
            "Retained Earnings Total Equity"
        ])
        total_liabilities = safe_get(balance, [
            "Total Liabilities Net Minority Interest",
            "Total Liabilities", "TotalLiabilities"
        ])

        # --- Market data from info ---
        market_cap    = info.get("marketCap", None)
        current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
        pe_ratio      = info.get("trailingPE", None)
        company_name  = info.get("longName", info.get("shortName", ticker))

        # Working capital = Current Assets - Current Liabilities
        working_capital = None
        if current_assets is not None and current_liabilities is not None:
            working_capital = current_assets - current_liabilities

        # Interest expense is usually reported as a negative number
        # in income statements — convert to positive for our calculations
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

        # Print a summary so the user can see what was fetched
        print(f"\n{'='*50}")
        print(f"  Live Data Fetched: {company_name} ({full_ticker})")
        print(f"{'='*50}")
        print(f"  Current Price     : ₹{current_price:,.2f}" if current_price else "  Current Price     : N/A")
        print(f"  Market Cap        : ₹{market_cap:,.0f}" if market_cap else "  Market Cap        : N/A")
        print(f"  EBIT              : ₹{ebit:,.0f}" if ebit else "  EBIT              : N/A")
        print(f"  Net Income        : ₹{net_income:,.0f}" if net_income else "  Net Income        : N/A")
        print(f"  Total Assets      : ₹{total_assets:,.0f}" if total_assets else "  Total Assets      : N/A")
        print(f"{'='*50}\n")

        return result

    except Exception as e:
        print(f"Error fetching data for {full_ticker}: {e}")
        return {}