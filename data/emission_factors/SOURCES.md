# Emission factor sources

All three are public. You may use any other **public** source as long as you cite it.

## 1. UK Government GHG Conversion Factors for Company Reporting 2024 (DESNZ)
- File: `UK_DESNZ_GHG_conversion_factors_2024_flat_v1.1.xlsx` — the official "flat file" (v1.1), unmodified. Sheet `Factors by Category`; header on row 6.
- Each factor exists per gas and in total: the row with `GHG/Unit = kg CO2e` is the total.
- Material factors (metals, plastics…) are under Level 1 `Material use`, per tonne; the column `Column Text` tells primary production from closed-loop (recycled) material.
- Publisher page and methodology paper: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024
- Licence: Open Government Licence v3.0.
- Note: built for UK reporting. Fuel, refrigerant, freight and material factors are commonly used internationally as proxies, but the **UK electricity factor is UK-specific**.

## 2. US EPA Supply Chain GHG Emission Factors for US Commodities and Industries, v1.3 (USEEIO)
- File: `US_EPA_SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv` — unmodified, by 2017 NAICS 6-digit code.
- Unit: **kg CO2e per 2022 US dollar, purchaser price**. "With margins" includes the transport and wholesale/retail margins.
- Dataset: https://doi.org/10.23719/1531143 (EPA Science Inventory / data.gov)
- Licence: public domain (US Government work).
- Note: a US economy model. Using it for European or Mexican purchases is a common proxy, and has known limits.

## 3. Ember — Yearly electricity data
- File: `Ember_electricity_CO2_intensity_2021_2024.csv` — extract of Ember's yearly full release, filtered on `Variable = CO2 intensity`, countries only, years 2021–2024. Values in gCO2(e) per kWh generated.
- Source and methodology: https://ember-energy.org/data/yearly-electricity-data/
- Licence: CC-BY-4.0 (Ember).
- Note: read Ember's methodology to know what the intensity includes before using it for scope 2.

## Reference data (`../reference/`)
- `fx_ECB_annual_average_2022_2024.csv` — ECB euro foreign exchange reference rates, annual averages (units of currency per 1 EUR). Source: ECB Data Portal, series `EXR.A.<CUR>.EUR.SP00.A`.
- `US_CPI-U_annual_average_2022_2024.csv` — US Consumer Price Index for All Urban Consumers (BLS series CUUR0000SA0), annual average of monthly values. Source: FRED series CPIAUCNS.
