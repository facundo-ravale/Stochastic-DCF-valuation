import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === STEP 1: INPUT BASE VALUES MANUALLY ===
def get_manual_inputs():
    print("Enter base (t=0) values for the company:")
    base_values = {
        'Revenue': float(input("Revenue: ")),
        'COGS': float(input("Cost of Goods Sold: ")),
        'Opex': float(input("Operating Expenses: ")),
        'D&A': float(input("Depreciation & Amortization: ")),
        'ΔReceivables': float(input("ΔReceivables: ")),
        'ΔInventory': float(input("ΔInventory: ")),
        'ΔPayables': float(input("ΔPayables: ")),
        'CapEx': float(input("Capital Expenditures: ")),
    }
    return base_values

# === STEP 2: GET GROWTH DISTRIBUTIONS ===
def get_distribution_inputs(elements):
    distributions = {}
    print("\nEnter expected MEAN and STD DEV of annual growth rate (in %) for each input:")
    for element in elements:
        while True:
            try:
                mean = float(input(f"  {element} - Mean growth rate (%): ")) / 100
                std = float(input(f"  {element} - Std dev (%): ")) / 100
                distributions[element] = (mean, std)
                break
            except ValueError:
                print("Invalid input. Please enter numeric values.")
    return distributions

# === STEP 3: CALCULATE WACC BASED ON ARGENTINA MARKET INPUTS ===
def calculate_wacc():
    print("\nEnter inputs for WACC calculation:")
    risk_free_rate = float(input("Risk-free rate (%): ")) / 100
    beta = float(input("Beta of the firm: "))
    equity_risk_premium = float(input("Equity market risk premium (%): ")) / 100
    country_risk_premium = float(input("Country risk premium (%): ")) / 100
    cost_of_debt = float(input("Cost of debt (%): ")) / 100
    tax_rate = float(input("Corporate tax rate (%): ")) / 100
    equity_value = float(input("Market value of equity: "))
    debt_value = float(input("Market value of debt: "))

    cost_of_equity = risk_free_rate + beta * (equity_risk_premium + country_risk_premium)
    total_value = equity_value + debt_value

    wacc = (equity_value / total_value) * cost_of_equity + (debt_value / total_value) * cost_of_debt * (1 - tax_rate)

    print(f"\nCalculated WACC: {wacc * 100:.2f}%")
    return wacc

# === STEP 4: MONTE CARLO SIMULATION ===
def monte_carlo_projection(base_values, distributions, wacc, shares_outstanding, cash, total_debt, years=5, n_simulations=10000):
    discounted_valuations = []
    annual_scenarios = {f"Year {i+1}": [] for i in range(years)}
    fcf_trajectories = []

    for _ in range(n_simulations):
        annuals = {k: [] for k in base_values.keys()}
        for k, base in base_values.items():
            mean, std = distributions[k]
            for i in range(years):
                growth = np.random.normal(loc=mean, scale=std)
                value = base * ((1 + growth) ** (i + 1))
                annuals[k].append(value)

        df = pd.DataFrame(annuals)
        df['Operating Income'] = df['Revenue'] - df['COGS'] - df['Opex']
        df['EBITDA'] = df['Operating Income'] + df['D&A']
        df['ΔWC'] = df['ΔReceivables'] + df['ΔInventory'] - df['ΔPayables']
        df['Operating CF'] = df['EBITDA'] - df['ΔWC']
        df['FCF'] = df['Operating CF'] - df['CapEx']

        fcf_trajectories.append(df['FCF'].values)

        for i in range(years):
            annual_scenarios[f"Year {i+1}"].append(df.iloc[i])

        discount_factors = [(1 / ((1 + wacc) ** (i + 1))) for i in range(years)]
        pv_fcf = sum(df['FCF'].iloc[i] * discount_factors[i] for i in range(years))

        # Add Terminal Value with g = 2.5%
        g = 0.025
        fcf_final = df['FCF'].iloc[-1]
        terminal_value = fcf_final * (1 + g) / (wacc - g)
        pv_terminal = terminal_value / ((1 + wacc) ** years)

        total_valuation = pv_fcf + pv_terminal
        discounted_valuations.append(total_valuation)

    discounted_valuations = np.array(discounted_valuations)
    ev_scenarios = {
        'Bearish (P20)': np.percentile(discounted_valuations, 20),
        'Neutral (Mean)': np.mean(discounted_valuations),
        'Bullish (P80)': np.percentile(discounted_valuations, 80)
    }

    equity_scenarios = {k.replace(')', ' - Equity)').replace('(', '(EV'): v - total_debt + cash for k, v in ev_scenarios.items()}
    valuation_per_share = {k.replace('Equity)', 'Equity / share)'): v / shares_outstanding for k, v in equity_scenarios.items()}
    valuation_scenarios = {**ev_scenarios, **equity_scenarios, **valuation_per_share}

    combined = {}
    fcf_stats = {'Bearish': [], 'Neutral': [], 'Bullish': []}
    for i, (year, records) in enumerate(annual_scenarios.items()):
        df_year = pd.DataFrame(records)
        summary = pd.DataFrame({
            f"Year {i+1} - Bearish (P20)": df_year.quantile(0.20),
            f"Year {i+1} - Neutral (Mean)": df_year.mean(),
            f"Year {i+1} - Bullish (P80)": df_year.quantile(0.80)
        })
        combined[f"Year {i+1}"] = summary
        fcf_stats['Bearish'].append(summary.loc['FCF'][f"Year {i+1} - Bearish (P20)"])
        fcf_stats['Neutral'].append(summary.loc['FCF'][f"Year {i+1} - Neutral (Mean)"])
        fcf_stats['Bullish'].append(summary.loc['FCF'][f"Year {i+1} - Bullish (P80)"])

    fcf_df = pd.DataFrame(fcf_stats, index=[f"Year {i+1}" for i in range(years)])

    return valuation_scenarios, combined, fcf_df, discounted_valuations

# === STEP 5: EXPORT RESULTS ===
def export_to_excel(base_values, valuation_scenarios, combined_scenarios, fcf_df, discounted_valuations, filename):
    base_df = pd.DataFrame.from_dict(base_values, orient='index', columns=['t=0'])
    scen_df = pd.DataFrame.from_dict(valuation_scenarios, orient='index', columns=['Valuation'])

    with pd.ExcelWriter(filename) as writer:
        base_df.to_excel(writer, sheet_name="Valuation", startrow=0)
        scen_df.to_excel(writer, sheet_name="Valuation", startrow=len(base_df) + 2)
        fcf_df.to_excel(writer, sheet_name="FCF_Projection")

        flat_combined = pd.concat(combined_scenarios.values(), axis=1)
        flat_combined.to_excel(writer, sheet_name="Projection_All")

        wacc_range = np.linspace(0.05, 0.15, 11)
        g_range = np.linspace(0.01, 0.05, 5)
        last_fcf = fcf_df.loc['Year 5']['Neutral']
        sens_matrix = pd.DataFrame(index=[f"g={g:.2%}" for g in g_range], columns=[f"WACC={w:.2%}" for w in wacc_range])

        for g in g_range:
            for w in wacc_range:
                tv = last_fcf * (1 + g) / (w - g)
                pv_tv = tv / ((1 + w) ** 5)
                total_valuation = pv_tv
                sens_matrix.loc[f"g={g:.2%}", f"WACC={w:.2%}"] = round(total_valuation, 2)

        sens_matrix.to_excel(writer, sheet_name="Sensitivity_Table")

# === STEP 6: PLOT FCF ===
def plot_fcf(fcf_df):
    plt.figure(figsize=(10, 6))
    for col in fcf_df.columns:
        plt.plot(fcf_df.index, fcf_df[col], label=col)
    plt.title("FCF Projection Across Scenarios")
    plt.xlabel("Year")
    plt.ylabel("FCF")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("fcf_projection_chart.png")
    plt.show()

# === MAIN FUNCTION ===
def run_model():
    base_values = get_manual_inputs()
    distributions = get_distribution_inputs(base_values.keys())
    wacc = calculate_wacc()
    shares_outstanding = float(input("Enter number of shares outstanding: "))
    cash = float(input("Enter cash: "))
    total_debt = float(input("Enter total debt (short + long term): "))

    valuation_scenarios, combined_scenarios, fcf_df, discounted_valuations = monte_carlo_projection(
        base_values, distributions, wacc, shares_outstanding, cash, total_debt
    )
    export_to_excel(base_values, valuation_scenarios, combined_scenarios, fcf_df, discounted_valuations, "montecarlo_valuation_summary.xlsx")
    plot_fcf(fcf_df)
    print("\nValuation completed. Output saved to montecarlo_valuation_summary.xlsx and FCF chart generated.")

if __name__ == "__main__":
    run_model()