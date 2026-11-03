import pandas as pd
import calendar
import numpy as np

QUARTER_MONTHS = {
    1: [1, 2, 3],
    2: [4, 5, 6],
    3: [7, 8, 9],
    4: [10, 11, 12],
}

COUNTRY_ISO2 = {
    'France': 'FR',
    'FR': 'FR',
    'Deutschland': 'DE',
    'POL': 'PL',
    'Mexico': 'MX',
    'USA': 'US'
}

CHEMNITZ_GO_VALID = True

ember_yearly = 'https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv'
ember_monthly = 'https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_monthly_global.csv'
AIB_residual = "https://www.aib-net.org/sites/default/files/assets/eecs/Residual%20Mix/2024_Final%20_Residual%20mix%20calculation%20results_30052025.xlsx"
sites_link = "data/client/kestrel_sites.xlsx"
material_group_link = "data/client/kestrel_material_groups.xlsx"
electricty_link = "data/client/kestrel_electricity_2024.xlsx"
ap_ledger_link = "data/client/kestrel_ap_ledger_2024.csv"

# ember yearly emissions grid data (200 countries) - uses full lifecycle emissions in intensity
grid_emit_df = pd.read_csv(ember_yearly)
# ember monthly emissions grid data - uses full lifecycle emissions in intensity
grid_emit_df_2 = pd.read_csv(ember_monthly)
# AIB residual mix
aib_mix = pd.read_excel(AIB_residual, sheet_name="CO2", index_col=0)

aib_mix.index.name = "Country"
aib_mix = aib_mix.reset_index()
aib_mix = aib_mix.rename(columns={"Production mix CO2": "prod_factor_g_per_kwh",
                                  "Residual mix CO2": "res_factor_g_per_kwh"})
aib_mix = aib_mix[["Country","prod_factor_g_per_kwh", "res_factor_g_per_kwh"]]

mex_mix = pd.DataFrame({
        "Country": ["MX"],
        "prod_factor_g_per_kwh": [444.0],
        "res_factor_g_per_kwh": [444.0]
    })

# Both are in CO2 lb/MWh
# Production -> 2023 CO2 (https://www.epa.gov/egrid/summary-data)
# Residual -> 2023 Adjusted System Mix (https://resource-solutions.org/2025-residual-mix/)
sc_mix = pd.DataFrame({
        "Country": ["US"],
        "prod_factor_g_per_kwh": [593.419 * 0.45359237],
        "res_factor_g_per_kwh": [601.8887958 * 0.45359237]
    })
aib_mix = pd.concat([mex_mix, sc_mix, aib_mix], ignore_index=True)

sites = pd.read_excel(sites_link)
# ledger_df = pd.read_csv(ap_ledger_link)
electric_sheets_dict = pd.read_excel(electricty_link, sheet_name=None)

frames = []
for name, df in electric_sheets_dict.items():
    df["City"] = name
    df['Ele_consume_kwh'] = df.iloc[:, 1]
    df['Ele_consume_kwh'] = pd.to_numeric(df['Ele_consume_kwh'], errors="coerce")

    if name == 'Roanne':
        df['Ele_consume_kwh'] = df['Ele_consume_kwh'] * 1000

    if name == 'Greenville':
        jan_mar = pd.DataFrame({
            'City': 'Greenville',
            "Month": [1, 2, 3],
            "Ele_consume_kwh": 0})
        df = pd.concat([jan_mar, df], ignore_index=True)

    if name == 'Katowice':
        df.index = df.index + 1
        df["Month"] = df.index.map(QUARTER_MONTHS)
        df = df.explode("Month").reset_index()
        df['Ele_consume_kwh'] = df['Ele_consume_kwh'] / 3
    else:
        df['Month'] = df.index + 1

    df['GO_per_cover'] = np.where((df["City"] == "Chemnitz") & (df["Month"] > 6) & CHEMNITZ_GO_VALID, 100, 0)
    df = df[['City', 'Ele_consume_kwh', 'Month', 'GO_per_cover']]
    df = df.head(12)
    df["Month"] = df["Month"].map(lambda m: calendar.month_name[m])
    df['Year'] = "2024"
    frames.append(df)

electricity_df = pd.concat(frames, ignore_index=True)

sites['Country'] = sites["Country"].map(COUNTRY_ISO2)
sites[["City", "State"]] = sites["City"].str.split(",", n=1, expand=True)
sites["City"] = (
    sites["City"].str.strip()
    .str.normalize("NFKD")
    .str.encode("ascii", "ignore")
    .str.decode("ascii")
)
sites["State"] = sites["State"].str.strip()
print(sites['Country'].unique())

electricity_df = electricity_df.merge(sites, on="City", how="left")
print(electricity_df['Country'].unique())
aib_mix = aib_mix[["Country", "prod_factor_g_per_kwh", "res_factor_g_per_kwh"]]

scope_2 = electricity_df.merge(aib_mix, on="Country", how="left")
scope_2['location_based'] = scope_2["Ele_consume_kwh"] * scope_2["prod_factor_g_per_kwh"] / 1_000_000

scope_2['market_based'] = (1 - scope_2['GO_per_cover'] / 100) * (scope_2["Ele_consume_kwh"] * scope_2["res_factor_g_per_kwh"] / 1_000_000)

by_country = scope_2.groupby("Country")[["Ele_consume_kwh", 'location_based', 'market_based']].sum()
by_corporate = scope_2[["Ele_consume_kwh", 'location_based', 'market_based']].sum()

print(by_country.head())
print(by_corporate.head())
# print(residual_mix_df.shape)
# column names
# print(residual_mix_df.columns)


# Residual: CO2 emission intensity is in gCO2/kWh
# Residual: AT, NL, CH have NaN values because they require suppliers to disclose
# print(electricity_df.columns)
print(electricity_df['City'].unique())
# null values per column and number of rows

# Scope 3 - spend data
# Total spend
# 80-90% of Spend Concentration
# Negative amounts
# Currencies
# Spend categories
# Dates (reporting year?)

# Scope 2 - electrical data
# Units match
# Country coverage
# Contractual Data?
