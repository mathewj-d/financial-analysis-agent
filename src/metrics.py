import numpy as np

def calculate_coefficient_of_variation(returns: list) -> float:
    """
    Calculates the Coefficient of Variation (CV) — a risk-to-reward ratio.
    
    CV = Standard Deviation / Mean Return
    Higher CV = more risk per unit of return (worse risk profile)
    Lower CV = more efficient risk-adjusted returns (better)
    """
    if not returns:
        return 0.0
    
    standard_deviation = np.std(returns)
    mean_return = np.mean(returns)
    
    if mean_return == 0:
        return 0.0
    
    return standard_deviation / mean_return


def analyze_earnings_structure(ebit: float, interest: float, tax_rate: float) -> dict:
    """
    Breaks down a company's corporate earnings structure.
    
    EBIT  = Earnings Before Interest and Tax
    EBT   = Earnings Before Tax (EBIT minus interest)
    EAT   = Earnings After Tax (what the company actually takes home)
    ICR   = Interest Coverage Ratio (how easily the company covers its debt payments)
    """
    ebt = ebit - interest
    eat = ebt * (1 - tax_rate)
    
    interest_coverage_ratio = ebit / interest if interest > 0 else float('inf')
    
    return {
        "EBIT": ebit,
        "Interest": interest,
        "EBT": ebt,
        "Tax_Rate": tax_rate,
        "EAT": eat,
        "Interest_Coverage_Ratio": interest_coverage_ratio
    }


def calculate_operating_leverage(contribution_margin: float, ebit: float) -> float:
    """
    Degree of Operating Leverage (DOL).
    
    Measures how sensitive EBIT is to changes in sales.
    Higher DOL = riskier business (fixed costs dominate)
    """
    if ebit == 0:
        return 0.0
    return contribution_margin / ebit


def calculate_financial_leverage(ebit: float, interest: float) -> float:
    """
    Degree of Financial Leverage (DFL).
    
    Measures how sensitive EPS is to changes in EBIT.
    Higher DFL = more financial risk from debt.
    """
    ebt = ebit - interest
    if ebt == 0:
        return 0.0
    return ebit / ebt
def dupont_analysis(net_income: float, total_revenue: float,
                    total_assets: float, total_equity: float) -> dict:
    """
    DuPont Decomposition of Return on Equity (ROE).

    ROE = Net Profit Margin × Asset Turnover × Equity Multiplier

    This breaks ROE into three drivers so you can see WHERE
    profitability is coming from — and where the risk is.

    - Net Profit Margin : Profitability (how much of revenue becomes profit)
    - Asset Turnover    : Efficiency (how hard assets are working)
    - Equity Multiplier : Leverage (how much debt is amplifying returns)
    """
    if any(v is None or v == 0 for v in [total_revenue, total_assets, total_equity]):
        return {"error": "Insufficient data for DuPont analysis"}

    net_profit_margin  = net_income / total_revenue        # Profitability
    asset_turnover     = total_revenue / total_assets      # Efficiency
    equity_multiplier  = total_assets / total_equity       # Leverage

    roe = net_profit_margin * asset_turnover * equity_multiplier

    return {
        "Net_Profit_Margin" : net_profit_margin,
        "Asset_Turnover"    : asset_turnover,
        "Equity_Multiplier" : equity_multiplier,
        "ROE"               : roe,
        "ROE_Percentage"    : roe * 100
    }


def altman_z_score(working_capital: float, total_assets: float,
                   retained_earnings: float, ebit: float,
                   market_cap: float, total_liabilities: float,
                   total_revenue: float) -> dict:
    """
    Altman Z-Score — Bankruptcy Prediction Model (1968, modified for non-US firms).

    Uses 5 financial ratios weighted by their predictive power.
    Originally developed by Edward Altman at NYU.

    Components:
    X1 = Working Capital / Total Assets         (liquidity)
    X2 = Retained Earnings / Total Assets       (accumulated profitability)
    X3 = EBIT / Total Assets                    (operating efficiency)
    X4 = Market Cap / Total Liabilities         (market-based leverage)
    X5 = Total Revenue / Total Assets           (asset efficiency)

    Interpretation Zones:
    Z > 2.99  → Safe Zone   (low bankruptcy risk)
    1.81-2.99 → Grey Zone   (monitor closely)
    Z < 1.81  → Distress Zone (high bankruptcy risk)
    """
    if any(v is None for v in [working_capital, total_assets, retained_earnings,
                                ebit, market_cap, total_liabilities, total_revenue]):
        return {"error": "Insufficient data for Altman Z-Score"}

    if total_assets == 0 or total_liabilities == 0:
        return {"error": "Total assets or liabilities cannot be zero"}

    # Five ratios
    x1 = working_capital   / total_assets       # Liquidity
    x2 = retained_earnings / total_assets       # Accumulated profitability
    x3 = ebit              / total_assets       # Operating efficiency
    x4 = market_cap        / total_liabilities  # Market leverage
    x5 = total_revenue     / total_assets       # Asset efficiency

    # Z-Score formula (Altman 1968)
    z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)

    # Determine zone
    if z_score > 2.99:
        zone = "Safe Zone"
        interpretation = "Low bankruptcy risk. Financially healthy."
    elif z_score >= 1.81:
        zone = "Grey Zone"
        interpretation = "Moderate risk. Monitor closely."
    else:
        zone = "Distress Zone"
        interpretation = "High bankruptcy risk. Caution advised."

    return {
        "X1_Liquidity"        : x1,
        "X2_Profitability"    : x2,
        "X3_Operating_Eff"    : x3,
        "X4_Market_Leverage"  : x4,
        "X5_Asset_Efficiency" : x5,
        "Z_Score"             : z_score,
        "Zone"                : zone,
        "Interpretation"      : interpretation
    }