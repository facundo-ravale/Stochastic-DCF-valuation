# Stochastic-DCF-valuation
EN: Probabilistic DCF valuation model in Python for private companies in emerging markets. Combines traditional discounted cash flow logic with Monte Carlo simulation to capture uncertainty in key financial and operational drivers.

# Stochastic Valuation Model in Python

**Author:** Facundo Ravale  
**Language:** Python 3.10+  
**Scope:** Private equity valuation under uncertainty (Monte Carlo + DCF)

---

## 🧠 Overview
This repository contains a probabilistic valuation model that adapts the traditional Discounted Cash Flow (DCF) methodology to companies operating in uncertain environments—particularly private firms in emerging markets such as Argentina.

Instead of assuming fixed growth rates and margins, the model simulates thousands of potential trajectories for key financial drivers (revenues, costs, CapEx, working capital, etc.) using Monte Carlo simulation. The result is a **distribution of equity values** that better reflects uncertainty and risk.

---

## ⚙️ How to Run
1. Clone the repository:
```bash
git clone https://github.com/yourusername/stochastic-valuation-model.git
cd stochastic-valuation-model
```

2. Install required libraries:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python model.py
```

You will be prompted to enter:
- Base financial inputs (Revenue, Opex, CapEx, etc.)
- Distribution parameters (mean, std dev) for each input
- WACC components (rf, beta, ERP, CRP, tax rate, etc.)
- Shares outstanding, cash, total debt

The script will generate:
- A distribution of valuations
- Excel file with summary tables and sensitivity analysis
- FCF chart across scenarios

---

## 📘 Documentation
For a detailed explanation of assumptions, modeling logic, and methodological considerations, please refer to the PDF file:

📄 `docs/Guía Valuation.pdf`

This guide includes:
- Conceptual DCF breakdown
- Rationale behind stochastic modeling
- Macroeconomic and microeconomic drivers
- WACC structure for private firms in Argentina
- Limitations and caveats

---

## 📈 Example Output
- Valuation scenarios: P20 (bear), mean (neutral), P80 (bull)
- Projected FCF (5-year horizon)
- Sensitivity matrix (WACC vs g)

![FCF Chart](fcf_projection_chart.png)

---

## 📄 License
MIT License. You are free to use and adapt the code, but attribution is appreciated.

---

## 🤝 Contact
Feel free to reach out for feedback, collaboration, or implementation in real-world use cases:

📧 facundo.ravale@gmail.com  
📎 [LinkedIn](https://www.linkedin.com/in/facundo-ravale-alonso)
