import os
import sys
from anthropic import Anthropic
from metrics import (
    calculate_coefficient_of_variation,
    analyze_earnings_structure,
    calculate_operating_leverage,
    calculate_financial_leverage,
    dupont_analysis,
    altman_z_score
)
from data_fetcher import fetch_indian_stock


class FinancialAnalysisAgent:
    """
    AI-powered financial analysis agent.

    Supports two modes:
    1. LIVE MODE  : Fetches real data from NSE/BSE via yfinance
    2. MANUAL MODE: Uses manually provided financial figures
    """

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please set it before running the agent."
            )
        self.client = Anthropic(api_key=api_key)

    def analyze_live(self, ticker: str, exchange: str = "NSE",
                     historical_returns: list = None) -> str:
        """
        LIVE MODE: Fetches real NSE/BSE data and runs full analysis.

        Parameters:
        - ticker           : Stock symbol e.g. "RELIANCE", "TCS", "HDFCBANK"
        - exchange         : "NSE" or "BSE"
        - historical_returns: Optional list of past annual returns
        """
        # Default historical returns if not provided
        if historical_returns is None:
            historical_returns = [0.08, 0.12, -0.03, 0.15, 0.07]

        # Step 1: Fetch live data
        data = fetch_indian_stock(ticker, exchange)

        if not data:
            return "Failed to fetch stock data. Check ticker symbol and try again."

        # Step 2: Check if we have minimum required data
        required = ["ebit", "interest_expense", "net_income",
                    "total_revenue", "total_assets", "total_equity"]
        missing = [k for k in required if data.get(k) is None]

        if missing:
            print(f"Warning: Missing data fields: {missing}")
            print("Some metrics may not be calculated.")

        # Step 3: Run all metric calculations
        return self._run_analysis(data, historical_returns)

    def analyze_manual(self, company_name: str, ebit: float,
                       interest: float, tax_rate: float,
                       contribution_margin: float,
                       historical_returns: list,
                       net_income: float = None,
                       total_revenue: float = None,
                       total_assets: float = None,
                       total_equity: float = None,
                       total_liabilities: float = None,
                       working_capital: float = None,
                       retained_earnings: float = None,
                       market_cap: float = None) -> str:
        """
        MANUAL MODE: Accepts manually entered financial data.
        Backward compatible with original usage.
        """
        data = {
            "company_name"     : company_name,
            "ticker"           : "MANUAL",
            "ebit"             : ebit,
            "interest_expense" : interest,
            "net_income"       : net_income,
            "total_revenue"    : total_revenue,
            "total_assets"     : total_assets,
            "total_equity"     : total_equity,
            "total_liabilities": total_liabilities,
            "working_capital"  : working_capital,
            "retained_earnings": retained_earnings,
            "market_cap"       : market_cap,
            "current_price"    : None,
            "pe_ratio"         : None,
        }
        return self._run_analysis(data, historical_returns,
                                  tax_rate=tax_rate,
                                  contribution_margin=contribution_margin)

    def _run_analysis(self, data: dict, historical_returns: list,
                      tax_rate: float = 0.25,
                      contribution_margin: float = None) -> str:
        """
        Core analysis pipeline — runs metrics and calls Claude.
        Used internally by both live and manual modes.
        """
        company_name     = data.get("company_name", "Unknown Company")
        ebit             = data.get("ebit")
        interest         = data.get("interest_expense")
        net_income       = data.get("net_income")
        total_revenue    = data.get("total_revenue")
        total_assets     = data.get("total_assets")
        total_equity     = data.get("total_equity")
        total_liabilities= data.get("total_liabilities")
        working_capital  = data.get("working_capital")
        retained_earnings= data.get("retained_earnings")
        market_cap       = data.get("market_cap")
        current_price    = data.get("current_price")
        pe_ratio         = data.get("pe_ratio")

        # --- Run earnings structure if we have EBIT and interest ---
        earnings = {}
        if ebit and interest:
            earnings = analyze_earnings_structure(ebit, interest, tax_rate)

        # --- Coefficient of Variation ---
        cv = calculate_coefficient_of_variation(historical_returns)

        # --- Operating & Financial Leverage ---
        dol, dfl = None, None
        if contribution_margin and ebit:
            dol = calculate_operating_leverage(contribution_margin, ebit)
        if ebit and interest:
            dfl = calculate_financial_leverage(ebit, interest)

        # --- DuPont Analysis ---
        dupont = {}
        if all(v is not None for v in [net_income, total_revenue, total_assets, total_equity]):
            dupont = dupont_analysis(net_income, total_revenue, total_assets, total_equity)

        # --- Altman Z-Score ---
        altman = {}
        if all(v is not None for v in [working_capital, total_assets, retained_earnings,
                                        ebit, market_cap, total_liabilities, total_revenue]):
            altman = altman_z_score(working_capital, total_assets, retained_earnings,
                                    ebit, market_cap, total_liabilities, total_revenue)

        # --- Build the prompt ---
        prompt = f"""
You are an elite institutional financial analyst at a top-tier investment bank covering Indian equities.

Analyze the following metrics for **{company_name}**:

--- MARKET DATA ---
{f"Current Price    : ₹{current_price:,.2f}" if current_price else "Current Price    : Manual input"}
{f"Market Cap       : ₹{market_cap:,.0f}" if market_cap else ""}
{f"P/E Ratio        : {pe_ratio:.2f}x" if pe_ratio else ""}

--- EARNINGS STRUCTURE ---
{f"EBIT             : ₹{earnings.get('EBIT', ebit):,.0f}" if (earnings or ebit) else ""}
{f"Interest Expense : ₹{earnings.get('Interest', interest):,.0f}" if (earnings or interest) else ""}
{f"EBT              : ₹{earnings.get('EBT'):,.0f}" if earnings.get('EBT') else ""}
{f"EAT              : ₹{earnings.get('EAT'):,.0f}" if earnings.get('EAT') else ""}
{f"ICR              : {earnings.get('Interest_Coverage_Ratio', 0):.2f}x (safe threshold >3.0x)" if earnings.get('Interest_Coverage_Ratio') else ""}

--- DUPONT DECOMPOSITION ---
{f"Net Profit Margin : {dupont.get('Net_Profit_Margin', 0)*100:.2f}% (profitability)" if dupont else "DuPont: Insufficient data"}
{f"Asset Turnover    : {dupont.get('Asset_Turnover', 0):.4f}x (efficiency)" if dupont else ""}
{f"Equity Multiplier : {dupont.get('Equity_Multiplier', 0):.2f}x (leverage)" if dupont else ""}
{f"ROE (DuPont)      : {dupont.get('ROE_Percentage', 0):.2f}%" if dupont else ""}

--- ALTMAN Z-SCORE (BANKRUPTCY RISK) ---
{f"Z-Score           : {altman.get('Z_Score', 0):.4f}" if altman else "Altman Z-Score: Insufficient data"}
{f"Zone              : {altman.get('Zone', '')}" if altman else ""}
{f"Interpretation    : {altman.get('Interpretation', '')}" if altman else ""}

--- RISK METRICS ---
{f"Coefficient of Variation (CV) : {cv:.4f} (lower = better risk-adjusted returns)" if cv else ""}
{f"Degree of Operating Leverage  : {dol:.2f}x" if dol else ""}
{f"Degree of Financial Leverage  : {dfl:.2f}x" if dfl else ""}
Historical Returns: {historical_returns}
Average Return    : {sum(historical_returns)/len(historical_returns)*100:.2f}%

Your task — write an institutional-grade executive brief covering:
1. Overall financial health (2-3 sentences)
2. DuPont insight — what is driving ROE? Is it margin, efficiency, or leverage? (2-3 sentences)
3. Bankruptcy risk assessment based on Altman Z-Score (1-2 sentences)
4. Leverage risk — operating and financial (1-2 sentences)
5. Final stance: Strong Buy / Buy / Hold / Avoid — one-line rationale

Be direct, blunt, and institutional. No fluff. Focus on Indian market context.
"""

        # --- Call Claude ---
        print("Sending to Claude for analysis...\n")
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text


def main():
    """
    Entry point. 
    
    Usage:
        python src/agent.py              → runs with sample manual data
        python src/agent.py RELIANCE     → fetches live NSE data for Reliance
        python src/agent.py TCS BSE      → fetches live BSE data for TCS
    """
    agent = FinancialAnalysisAgent()

    # Check if a ticker was passed as command-line argument
    if len(sys.argv) >= 2:
        ticker   = sys.argv[1]
        exchange = sys.argv[2] if len(sys.argv) >= 3 else "NSE"

        print(f"\nLIVE MODE: Fetching {ticker} from {exchange}")
        result = agent.analyze_live(ticker, exchange)

    else:
        # No ticker provided — use sample data
        print("\nMANUAL MODE: Using sample data (no ticker provided)")
        print("Tip: Run 'python src/agent.py RELIANCE' for live NSE data\n")

        result = agent.analyze_manual(
            company_name        = "Hypothetical Industries Ltd. (India)",
            ebit                = 2_500_000,
            interest            = 400_000,
            tax_rate            = 0.25,
            contribution_margin = 3_200_000,
            historical_returns  = [0.08, 0.12, -0.03, 0.15, 0.07, -0.01, 0.10],
            net_income          = 1_575_000,
            total_revenue       = 8_000_000,
            total_assets        = 12_000_000,
            total_equity        = 6_000_000,
            total_liabilities   = 6_000_000,
            working_capital     = 1_500_000,
            retained_earnings   = 3_200_000,
            market_cap          = 15_000_000
        )

    print("\n" + "="*60)
    print("   FINANCIAL ANALYSIS AGENT — EXECUTIVE REPORT")
    print("="*60)
    print(result)
    print("="*60 + "\n")


if __name__ == "__main__":
    main()