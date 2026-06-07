# 📊 Financial Analysis Agent — Open Source AI Tool

An autonomous AI agent that takes raw corporate financial data, computes institutional-grade risk and leverage metrics, and generates executive-quality analysis reports using Claude.

Built for finance professionals, students, and developers who want AI-assisted financial due diligence without a Bloomberg terminal.

---

## 🧠 What It Does

| Step | Action |
|------|--------|
| 1 | Accepts raw EBIT, interest, tax rate, and historical return data |
| 2 | Computes CV, ICR, DOL, DFL using pure financial formulas |
| 3 | Sends structured metrics to Claude via the Anthropic API |
| 4 | Returns an institutional-grade executive risk report |

---

## 📐 Metrics Calculated

| Metric | Formula | What It Tells You |
|--------|---------|-------------------|
| **Interest Coverage Ratio (ICR)** | EBIT ÷ Interest | Can the company pay its debt? |
| **Coefficient of Variation (CV)** | Std Dev ÷ Mean Return | Risk per unit of return |
| **Degree of Operating Leverage (DOL)** | Contribution Margin ÷ EBIT | Sensitivity to sales changes |
| **Degree of Financial Leverage (DFL)** | EBIT ÷ EBT | Sensitivity to EBIT changes |
| **EAT (Net Earnings After Tax)** | (EBIT − Interest) × (1 − tax rate) | Actual take-home earnings |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/mathewj-d/financial-analysis-agent.git
cd financial-analysis-agent
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your Anthropic API Key
```bash
# Windows
set ANTHROPIC_API_KEY=your-key-here

# Mac/Linux
export ANTHROPIC_API_KEY=your-key-here
```
Get your API key at: https://console.anthropic.com

### 5. Run the agent
```bash
python src/agent.py
```

---

## 📋 Sample Output
============================================================
FINANCIAL ANALYSIS AGENT — EXECUTIVE REPORT
Hypothetical Industries Ltd. demonstrates a solid earnings base with EAT
of ₹15.75L against a controlled interest burden. The ICR of 6.25x is
comfortably above the 3.0x safety threshold, indicating low immediate
debt-service risk.
Operating leverage (DOL: 1.28x) is moderate, suggesting the company
is not overly exposed to fixed-cost drag. Financial leverage (DFL: 1.19x)
is conservative — EPS volatility from EBIT swings remains manageable.
Return consistency shows moderate variance (CV: 0.6134) with a positive
average of 6.86% — acceptable for a mid-cap industrial.
Stance: BUY — Solid fundamentals with controlled leverage. Monitor
working capital cycles in next reporting period.
============================================================
---

## 🛠️ Roadmap

- [ ] Add PDF parser for corporate 10-K and Indian Annual Report filings
- [ ] Integrate NSE/BSE live data via APIs for real-time ICR tracking
- [ ] Expand to multi-company comparative analysis
- [ ] Add DuPont decomposition and Altman Z-Score modules
- [ ] Build a simple Streamlit dashboard for non-technical users
- [ ] Export reports to PDF and Word format

---

## 🧩 Project Structure
financial-analysis-agent/
├── src/
│   ├── init.py        # Package marker
│   ├── agent.py           # Claude API orchestration and main pipeline
│   └── metrics.py         # Pure financial formula engine
├── data/
│   └── sample_input.json  # Example corporate financial inputs
├── requirements.txt        # Python dependencies
└── README.md
---

## 💡 Use Cases

- **Finance students** — Run real-world company data from annual reports
- **Investment analysts** — Quick risk screening tool before deep dives
- **Corporate finance teams** — Automate preliminary assessment reports
- **Educators** — Demonstrate financial ratios with AI-generated explanations

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.
If you use this for academic or professional work, a star ⭐ is appreciated.
