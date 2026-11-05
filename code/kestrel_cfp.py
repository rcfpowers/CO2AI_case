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

UNIT_TO_KG = {"to": 1000, "t": 1000, "kg": 1}

# Aluminium Primary: "19_504_5104_15_1"
# Steel Primary: "19_504_5119_15_1"
# PP Primary: "19_505_5147_15_1"
DESNZ_MAP = {
    "MG-ALU-ING": "19_504_5107_15_1",   # Metal: aluminium cans and foil (excl. forming) Closet Loop
    "MG-STL-COIL": "19_504_5116_15_1",  # Metal: steel cans Closet Loop
    "MG-PLA-PP": "19_505_5144_15_1",    # Plastics: PP (incl. forming) Closet Loop
}

NAICS_MAP = {
    "MG-RUBB": 326291,
    "MG-FAST": 332722,
    "MG-PAINT": 325510,
    "MG-PLA-PA": 325991,
    "MG-ELEC": 336320,
    "MG-MACH": 332710,
    "MG-PACK": 322211,
    "MG-MRO": 811310,
    "MG-TEMP": 561320,
    "MG-CONS": 541611,
    "MG-IT": 518210,
    "MG-FAC": 561720,
}

KATOWICE_Q4_ESTIMATE = True
CHEMNITZ_GO_VALID = True
REPORTING_YEAR = 2024
USD_PER_EUR_2024 = 1.08238

MATGROUP_SET_ASIDE = {
    "MG-ENER": "Energy: electricity in Scope 2, gas in Scope 1",
    "MG-LOG": "Freight: Scope 3 Category 4",
    "MG-TRAV": "Business travel: Scope 3 Category 6",
    "MG-CAPEX-MACH": "Capital goods: Scope 3 Category 2",
    "MG-CAPEX-TOOL": "Capital goods: Scope 3 Category 2",
}

MATGROUP_CATEGORY = {
    "MG-ENER": "S2/S1",
    "MG-LOG": "S3.4",
    "MG-TRAV": "S3.6",
    "MG-CAPEX-MACH": "S3.2",
    "MG-CAPEX-TOOL": "S3.2",
}

# Data source links
ember_yearly = 'data/emission_factors/Ember_electricity_CO2_intensity_2021_2024.csv'
AIB_residual = "https://www.aib-net.org/sites/default/files/assets/eecs/Residual%20Mix/2024_Final%20_Residual%20mix%20calculation%20results_30052025.xlsx"
sites_link = "data/client/kestrel_sites.xlsx"
material_group_link = "data/client/kestrel_material_groups.xlsx"
electricty_link = "data/client/kestrel_electricity_2024.xlsx"
ap_ledger_link = "data/client/kestrel_ap_ledger_2024.csv"
euro_conversion_link = "data/reference/fx_ECB_annual_average_2022_2024.csv"
material_group_link = "data/client/kestrel_material_groups.xlsx"
desnz_link = "data/emission_factors/UK_DESNZ_GHG_conversion_factors_2024_flat_v1.1.xlsx"
epa_sc_link = "data/emission_factors/US_EPA_SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv"
cpi_link = "data/reference/US_CPI-U_annual_average_2022_2024.csv"

results = pd.DataFrame({})

# SCOPE 2 CALCULATIONS

# Scope 2 Emissions dataframes
# Ember yearly emissions grid data (200 countries) - uses full lifecycle emissions in intensity
grid_emit_df = pd.read_csv(ember_yearly)

# AIB residual mix
# Residual mix and production EF -> https://www.aib-net.org/facts/european-residual-mix/2024
aib_mix = pd.read_excel(AIB_residual, sheet_name="CO2", index_col=0)
aib_mix.index.name = "Country"
aib_mix = aib_mix.reset_index()
aib_mix = aib_mix.rename(columns={"Production mix CO2": "prod_factor_g_per_kwh",
                                  "Residual mix CO2": "res_factor_g_per_kwh"})
aib_mix = aib_mix[["Country","prod_factor_g_per_kwh", "res_factor_g_per_kwh"]]
aib_mix['res_ef_source'] = 'https://www.aib-net.org/facts/european-residual-mix/2024'
aib_mix['prod_ef_source'] = 'https://www.aib-net.org/facts/european-residual-mix/2024'
aib_mix['ef_id'] = aib_mix['Country']

# Mexican Grid data
# No residual mix data for Mexico
# Annual Grid data for 2024 Provided by national government -> https://www.gob.mx/cms/uploads/attachment/file/981194/aviso_fesen_2024.pdf
# Unit: tCO2e/ Mwh
# Value: 0.444 tCO2e / MWh
mex_mix = pd.DataFrame({
        "Country": ["MX"],
        "prod_factor_g_per_kwh": [444.0],
        "res_factor_g_per_kwh": [444.0],
        'res_ef_source': 'https://www.gob.mx/cms/uploads/attachment/file/981194/aviso_fesen_2024.pdf',
        'prod_ef_source': 'https://www.gob.mx/cms/uploads/attachment/file/981194/aviso_fesen_2024.pdf',
        'ef_id': ''
    })

# US Grid data
# Production and residual EFs are in CO2 lb/MWh
# 0.45359237 is conversion of lb/MWh -> g/kWh
# Production -> 2023 CO2 (https://www.epa.gov/egrid/summary-data)
# Residual -> 2023 Adjusted System Mix (https://resource-solutions.org/2025-residual-mix/)
# SRVC Production Grid CO2 EF: 593.419 lb/MWh
# SRVC Adjusted System Mix CO2 EF: 601.8887958 lb/MWh
sc_mix = pd.DataFrame({
        "Country": ["US"],
        "prod_factor_g_per_kwh": [593.419 * 0.45359237],
        "res_factor_g_per_kwh": [601.8887958 * 0.45359237],
        'res_ef_source': 'https://resource-solutions.org/2025-residual-mix/',
        'prod_ef_source': 'https://www.epa.gov/egrid/summary-data',
        'ef_id': 'SRVC'
    })

aib_mix = pd.concat([mex_mix, sc_mix, aib_mix], ignore_index=True)

# Reading site level data for electricity use, each site has its own sheet in excel file
sites = pd.read_excel(sites_link)
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

katowice = electricity_df["City"] == "Katowice"
missing = katowice & electricity_df["Ele_consume_kwh"].isna()

if KATOWICE_Q4_ESTIMATE:
    q1_q3_average = electricity_df.loc[katowice & ~missing, "Ele_consume_kwh"].mean()
    electricity_df.loc[missing, "Ele_consume_kwh"] = q1_q3_average

sites['Country'] = sites["Country"].map(COUNTRY_ISO2)
sites[["City", "State"]] = sites["City"].str.split(",", n=1, expand=True)
sites["City"] = (
    sites["City"].str.strip()
    .str.normalize("NFKD")
    .str.encode("ascii", "ignore")
    .str.decode("ascii")
)
sites["State"] = sites["State"].str.strip()

electricity_df = electricity_df.merge(sites, on="City", how="left")

scope_2 = electricity_df.merge(aib_mix, on="Country", how="left")
scope_2['location_based'] = scope_2["Ele_consume_kwh"] * scope_2["prod_factor_g_per_kwh"] / 1000

scope_2['market_based'] = (1 - scope_2['GO_per_cover'] / 100) * (scope_2["Ele_consume_kwh"] * scope_2["res_factor_g_per_kwh"] / 1000)

location = scope_2.assign(
    scope2_method="location",
    ef_value=scope_2["prod_factor_g_per_kwh"] / 1000,
    emissions_kgco2e=scope_2["location_based"],
    quantity=scope_2["Ele_consume_kwh"],
    city=scope_2["City"],
    month=scope_2["Month"],
    ef_source=scope_2['prod_ef_source'],
    ef_id=scope_2['ef_id']
)
market = scope_2.assign(
    scope2_method="market",
    ef_value=(1 - scope_2["GO_per_cover"] / 100) * (scope_2["res_factor_g_per_kwh"] / 1000),
    emissions_kgco2e=scope_2["market_based"],
    quantity=scope_2["Ele_consume_kwh"],
    city=scope_2["City"],
    month=scope_2["Month"],
    ef_source=scope_2['res_ef_source'],
    ef_id=scope_2['ef_id']
)

results = pd.concat([location, market], ignore_index=True).drop(
    columns=["location_based", "market_based"]
)

results['source_file'] = 'kestrel_electricity_2024.xlsx'
results['source_reference'] = results["city"] + "/" + results["month"] + "24"
results['category'] = "S2"
results['status'] = "included"
results['description'] = 'Electricity'
results['method'] = 'activity-based'
results['unit'] = 'kWh'
results['ef_unit'] = 'kgCO2e/kWh'
results['site_code'] = ''
results['spend_eur'] = ''

results = results[['source_file', 'source_reference', 'site_code', 'category', 'status',
                   'scope2_method', 'description', 'quantity', 'unit', 'spend_eur', 'method',
                   'ef_source', 'ef_id', 'ef_value', 'ef_unit', 'emissions_kgco2e']]


# SCOPE 3.1 CALCULATIONS

ap_ledger = pd.read_csv(ap_ledger_link, sep=";")
material_groups = pd.read_excel(material_group_link)
desnz = pd.read_excel(desnz_link, sheet_name="Factors by Category", header=5)
euro_conversion = pd.read_csv(euro_conversion_link)
epa_sc = pd.read_csv(epa_sc_link)
cpi = pd.read_csv(cpi_link)

cpi = cpi.rename(columns={"CPI-U (1982-84=100), annual average": "cpi"})
euro_conversion = euro_conversion.rename(columns={"year": "Year",
                                                  "currency": "Currency"})

cpi_2022 = cpi.loc[cpi["year"] == 2022, "cpi"].iloc[0]
cpi_2024 = cpi.loc[cpi["year"] == 2024, "cpi"].iloc[0]

CPI_22_24 = cpi_2022 / cpi_2024

desnz = desnz[desnz["ID"].isin(DESNZ_MAP.values())]

ap_ledger["PostingDate"] = pd.to_datetime(ap_ledger["PostingDate"], format="%d.%m.%Y", errors="coerce")
ap_ledger['Year'] = ap_ledger["PostingDate"].dt.year

ledger_24 = ap_ledger[ap_ledger['Year'] == REPORTING_YEAR]
ledger_24 = ledger_24.merge(euro_conversion, on=['Currency', 'Year'], how="left")
ledger_24['units_per_EUR'] = ledger_24['units_per_EUR'].fillna(1)
ledger_24['NetAmount_EUR'] = ledger_24['NetAmount'] / ledger_24['units_per_EUR']
ledger_24['NetAmount_USD_24'] = ledger_24['NetAmount_EUR'] * USD_PER_EUR_2024
ledger_24['NetAmount_USD_22'] = ledger_24['NetAmount_USD_24'] * CPI_22_24

ledger_Mat_Null = ledger_24[ledger_24["MatGroup"].isnull()]
ledger_24 = ledger_24[ledger_24["MatGroup"].notnull()]

ledger_24 = ledger_24.merge(material_groups, on="MatGroup", how="left")

ledger_24["kg_per_unit"] = ledger_24["UoM"].str.lower().map(UNIT_TO_KG)
ledger_24["Qty_t"] = ledger_24["Qty"] * ledger_24["kg_per_unit"] / 1000

ledger_24["set_aside_reason"] = ledger_24["MatGroup"].map(MATGROUP_SET_ASIDE)
category_1 = ledger_24[ledger_24["set_aside_reason"].isna()]
set_aside = ledger_24[ledger_24["set_aside_reason"].notna()]

bridge = pd.DataFrame(DESNZ_MAP.items(), columns=["MatGroup", "ID"])

material_factors = bridge.merge(
    desnz[["ID", "Level 3", "Column Text", "GHG Conversion Factor 2024"]],
    on="ID", how="left",
).rename(columns={"GHG Conversion Factor 2024": "factor_kg_per_t"})

category_1 = category_1.merge(material_factors, on="MatGroup", how="left")

epa_sc = epa_sc[['2017 NAICS Code', '2017 NAICS Title', 'Supply Chain Emission Factors with Margins']]
epa_sc = epa_sc.rename(columns={'2017 NAICS Code': 'NAICS_Code',
                                '2017 NAICS Title': 'NAICS_Title',
                                'Supply Chain Emission Factors with Margins': 'kg_emit_per_22_USD'})

category_1["NAICS_Code"] = category_1["MatGroup"].map(NAICS_MAP)

category_1 = category_1.merge(epa_sc, on="NAICS_Code", how="left")

spend_based = category_1["factor_kg_per_t"].isna()

category_1.loc[spend_based, "emissions_kg"] = (
    category_1.loc[spend_based, "NetAmount_USD_22"] * category_1.loc[spend_based, "kg_emit_per_22_USD"]
)
category_1.loc[~spend_based, "emissions_kg"] = (
    category_1.loc[~spend_based, "Qty_t"] * category_1.loc[~spend_based, "factor_kg_per_t"]
)
category_1["method"] = np.where(spend_based, "spend-based", "mass-based")

results_3_1 = category_1.copy()

results_3_1["UoM"] = results_3_1["UoM"].str.lower()
results_3_1.loc[results_3_1["UoM"] == "to", "UoM"] = "t"

results_3_1['source_file'] = 'kestrel_ap_ledger_2024.csv'
results_3_1['category'] = 'S3.1'
results_3_1['status'] = 'included'
results_3_1['site_code'] = ''

results_3_1["ef_source"] = np.where(
    results_3_1["method"] == "mass-based",
    "https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
    "https://doi.org/10.23719/1531143",
)

results_3_1["ef_unit"] = np.where(
    results_3_1["method"] == "mass-based",
    "kgCO2e/t",
    "kgCO2e/EUR",
)

results_3_1['ef_id'] = np.where(
    results_3_1["method"] == "mass-based",
    results_3_1['ID'],
    results_3_1["NAICS_Code"].astype("Int64").astype(str),
)

results_3_1["ef_value"] = np.where(
    results_3_1["method"] == "mass-based",
    results_3_1["factor_kg_per_t"],
    results_3_1[ "kg_emit_per_22_USD"],
)

results_3_1 = results_3_1.rename(columns={"DocNo": "source_reference",
                                          "Description": "description",
                                          "Qty": "quantity",
                                          "UoM": "unit", 
                                          "NetAmount_EUR": "spend_eur",
                                          "emissions_kg": "emissions_kgco2e"})

results_3_1 = results_3_1[['source_file', 'source_reference', 'site_code', 'category', 'status',
                           'description', 'quantity', 'unit', 'spend_eur', 'method',
                           'ef_unit', 'ef_id', 'ef_value', 'ef_source', 'emissions_kgco2e']]

set_aside['source_file'] = 'kestrel_ap_ledger_2024.csv'
set_aside["category"] = set_aside["MatGroup"].map(MATGROUP_CATEGORY)
set_aside['status'] = 'set aside'
set_aside['site_code'] = ''

set_aside = set_aside.rename(columns={"DocNo": "source_reference",
                                      "Description": "description",
                                      "Qty": "quantity",
                                      "UoM": "unit", 
                                      "NetAmount_EUR": "spend_eur",
                                      "set_aside_reason": "comment"})

set_aside = set_aside[['source_file', 'source_reference', 'site_code', 'category', 'status',
                       'description', 'quantity', 'unit', 'spend_eur', 'comment']]

results = pd.concat([results, results_3_1, set_aside], ignore_index=True)

results.to_csv("results.csv", index=False)
