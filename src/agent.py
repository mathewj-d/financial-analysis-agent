import os
import json
from anthropic import Anthropic
from metrics import (
    calculate_coefficient_of_variation,
    analyze_earnings_structure,
    calculate_operating_leverage,
    calculate_financial_leverage
)


class FinancialAnalysisAgent:
    """
    An AI-powered financial analysis agent that:
    1. Accepts raw corporate financial inputs
    2. Computes key risk and valuation metrics locally
    3. Sends those metrics to Claude to generate an executive-grade report
    """

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please set it before running the agent."
            )
        self.client = Anthropic(api_key=api_key)

    def analyze(
        self,
        company_name: str,
        ebit: float,
        interest: float,
        tax_rate: float,
        contribution_margin: float,
        historical_returns: list
    ) -> str:
        """
        Full financial analysis pipeline.
        Runs all metric calculations, then calls Claude for the narrative report.
        """
        
        # Step 1: Run all local financial calculations
        earnings = analyze_earnings_structure(ebit, interest, tax_rate)
        cv = calculate_coefficient_of_variation(historical_returns)
        dol = calculate_operating_leverage(contribution_margin, ebit)
        dfl = calculate_financial_leverage(ebit, interest)
        
        # Step 2: Format a structured prompt for Claude
        prompt = f"""
You are an elite institutional financial analyst at a top-tier investment bank.

Analyze the following pre-calculated financial metrics for **{company_name}**:

--- EARNINGS STRUCTURE ---
- EBIT: ₹{earnings['EBIT']:,.0f}
- Interest Expense: ₹{earnings['Interest']:,.0f}
- EBT (Earnings Before Tax): ₹{earnings['EBT']:,.0f}
- Tax Rate Applied: {earnings['Tax_Rate']*100:.1f}%
- EAT (Net Earnings After Tax): ₹{earnings['EAT']:,.0f}

--- RISK METRICS ---
- Interest Coverage Ratio (ICR): {earnings['Interest_Coverage_Ratio']:.2f}x
  (Industry safe threshold: >3.0x)
- Coefficient of Variation (CV): {cv:.4f}
  (Lower is better; measures risk per unit of return)
- Degree of Operating Leverage (DOL): {dol:.2f}x
- Degree of Financial Leverage (DFL): {dfl:.2f}x

--- HISTORICAL RETURNS ---
- Data points: {historical_returns}
- Average Return: {sum(historical_returns)/len(historical_returns)*100:.2f}%

Your task:
1. Assess the company's overall financial health (2-3 sentences)
2. Evaluate its leverage risk — both operating and financial (2-3 sentences)
3. Comment on return consistency using the CV and historical data (1-2 sentences)
4. Give a final investment stance: Strong Buy / Buy / Hold / Avoid — with a one-line rationale

Be blunt, concise, and institutional in tone. No fluff.
"""
        
        # Step 3: Call Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text


def main():
    """
    Demo run using a fictional Indian mid-cap company.
    """
    agent = FinancialAnalysisAgent()
    
    # Sample company data (all figures in INR)
    result = agent.analyze(
        company_name="Hypothetical Industries Ltd. (India)",
        ebit=2_500_000,           # ₹25 Lakhs EBIT
        interest=400_000,          # ₹4 Lakhs interest expense
        tax_rate=0.25,             # 25% tax rate
        contribution_margin=3_200_000,  # ₹32 Lakhs contribution margin
        historical_returns=[0.08, 0.12, -0.03, 0.15, 0.07, -0.01, 0.10]
    )
    
    print("\n" + "="*60)
    print("   FINANCIAL ANALYSIS AGENT — EXECUTIVE REPORT")
    print("="*60)
    print(result)
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
