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
