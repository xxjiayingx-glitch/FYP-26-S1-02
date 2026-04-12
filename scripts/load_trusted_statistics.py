# import sys
# import os
# import requests

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from entity.db_connection import get_db_connection

# SUPPORTED_INDICATORS = [
#     {
#         "metric_key": "singapore_inflation_rate",
#         "country_code": "SGP",
#         "indicator_code": "FP.CPI.TOTL.ZG",
#         "country": "Singapore",
#         "unit": "%",
#         "source_name": "World Bank",
#         "source_url": "https://data.worldbank.org/"
#     },
#     {
#         "metric_key": "singapore_unemployment_rate",
#         "country_code": "SGP",
#         "indicator_code": "SL.UEM.TOTL.ZS",
#         "country": "Singapore",
#         "unit": "%",
#         "source_name": "World Bank",
#         "source_url": "https://data.worldbank.org/"
#     },
#     {
#         "metric_key": "singapore_population",
#         "country_code": "SGP",
#         "indicator_code": "SP.POP.TOTL",
#         "country": "Singapore",
#         "unit": "people",
#         "source_name": "World Bank",
#         "source_url": "https://data.worldbank.org/"
#     },
#     {
#         "metric_key": "singapore_gdp_growth",
#         "country_code": "SGP",
#         "indicator_code": "NY.GDP.MKTP.KD.ZG",
#         "country": "Singapore",
#         "unit": "%",
#         "source_name": "World Bank",
#         "source_url": "https://data.worldbank.org/"
#     }
# ]


# def upsert_stat(metric_key, country, year, value, unit, source_name, source_url):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     sql = """
#     INSERT INTO Trusted_Statistics
#     (metric_key, country, year, value, unit, source_name, source_url)
#     VALUES (%s, %s, %s, %s, %s, %s, %s)
#     ON DUPLICATE KEY UPDATE
#         value = VALUES(value),
#         unit = VALUES(unit),
#         source_name = VALUES(source_name),
#         source_url = VALUES(source_url),
#         last_updated = CURRENT_TIMESTAMP
#     """

#     cursor.execute(sql, (metric_key, country, year, value, unit, source_name, source_url))
#     conn.commit()

#     print(f"Upserted {metric_key} ({country}, {year}) = {value}")

#     cursor.close()
#     conn.close()


# def fetch_indicator(country_code, indicator_code):
#     url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json"

#     response = requests.get(url, timeout=10)
#     response.raise_for_status()
#     data = response.json()

#     if not isinstance(data, list) or len(data) < 2 or not data[1]:
#         return None, None

#     records = data[1]

#     for record in records:
#         value = record.get("value")
#         year = record.get("date")

#         if value is not None and year is not None:
#             return float(value), int(year)

#     return None, None


# def load_data():
#     for indicator in SUPPORTED_INDICATORS:
#         value, year = fetch_indicator(
#             indicator["country_code"],
#             indicator["indicator_code"]
#         )

#         if value is not None and year is not None:
#             if indicator["unit"] == "%":
#                 value = round(value, 2)
#             elif indicator["unit"] == "people":
#                 value = round(value, 0)

#             upsert_stat(
#                 indicator["metric_key"],
#                 indicator["country"],
#                 year,
#                 value,
#                 indicator["unit"],
#                 indicator["source_name"],
#                 indicator["source_url"]
#             )
#         else:
#             print(f"No data retrieved for {indicator['metric_key']}")

#     print("Trusted statistics update completed.")


# if __name__ == "__main__":
#     load_data()

import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from entity.TrustedStatistics import TrustedStatistic

SUPPORTED_INDICATORS = [

    # ── ECONOMIC: Inflation ──────────────────────────────────────────────
    {"metric_key": "singapore_inflation_rate",   "country_code": "SGP", "indicator_code": "FP.CPI.TOTL.ZG", "country": "Singapore",     "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_inflation_rate",    "country_code": "MYS", "indicator_code": "FP.CPI.TOTL.ZG", "country": "Malaysia",      "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "usa_inflation_rate",         "country_code": "USA", "indicator_code": "FP.CPI.TOTL.ZG", "country": "United States", "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "china_inflation_rate",       "country_code": "CHN", "indicator_code": "FP.CPI.TOTL.ZG", "country": "China",         "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "uk_inflation_rate",          "country_code": "GBR", "indicator_code": "FP.CPI.TOTL.ZG", "country": "United Kingdom","unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_inflation_rate",      "country_code": "WLD", "indicator_code": "FP.CPI.TOTL.ZG", "country": "Global",        "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── ECONOMIC: Unemployment ───────────────────────────────────────────
    {"metric_key": "singapore_unemployment_rate","country_code": "SGP", "indicator_code": "SL.UEM.TOTL.ZS", "country": "Singapore",     "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_unemployment_rate", "country_code": "MYS", "indicator_code": "SL.UEM.TOTL.ZS", "country": "Malaysia",      "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "usa_unemployment_rate",      "country_code": "USA", "indicator_code": "SL.UEM.TOTL.ZS", "country": "United States", "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "china_unemployment_rate",    "country_code": "CHN", "indicator_code": "SL.UEM.TOTL.ZS", "country": "China",         "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_unemployment_rate",   "country_code": "WLD", "indicator_code": "SL.UEM.TOTL.ZS", "country": "Global",        "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── ECONOMIC: GDP Growth ─────────────────────────────────────────────
    {"metric_key": "singapore_gdp_growth",       "country_code": "SGP", "indicator_code": "NY.GDP.MKTP.KD.ZG", "country": "Singapore",     "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_gdp_growth",        "country_code": "MYS", "indicator_code": "NY.GDP.MKTP.KD.ZG", "country": "Malaysia",      "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "usa_gdp_growth",             "country_code": "USA", "indicator_code": "NY.GDP.MKTP.KD.ZG", "country": "United States", "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "china_gdp_growth",           "country_code": "CHN", "indicator_code": "NY.GDP.MKTP.KD.ZG", "country": "China",         "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "uk_gdp_growth",              "country_code": "GBR", "indicator_code": "NY.GDP.MKTP.KD.ZG", "country": "United Kingdom","unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_gdp_growth",          "country_code": "WLD", "indicator_code": "NY.GDP.MKTP.KD.ZG", "country": "Global",        "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── ECONOMIC: GDP Per Capita (USD) ───────────────────────────────────
    {"metric_key": "singapore_gdp_per_capita",   "country_code": "SGP", "indicator_code": "NY.GDP.PCAP.CD", "country": "Singapore",     "unit": "USD", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_gdp_per_capita",    "country_code": "MYS", "indicator_code": "NY.GDP.PCAP.CD", "country": "Malaysia",      "unit": "USD", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "usa_gdp_per_capita",         "country_code": "USA", "indicator_code": "NY.GDP.PCAP.CD", "country": "United States", "unit": "USD", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "china_gdp_per_capita",       "country_code": "CHN", "indicator_code": "NY.GDP.PCAP.CD", "country": "China",         "unit": "USD", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_gdp_per_capita",      "country_code": "WLD", "indicator_code": "NY.GDP.PCAP.CD", "country": "Global",        "unit": "USD", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── POPULATION ───────────────────────────────────────────────────────
    {"metric_key": "singapore_population",       "country_code": "SGP", "indicator_code": "SP.POP.TOTL", "country": "Singapore",     "unit": "people", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_population",        "country_code": "MYS", "indicator_code": "SP.POP.TOTL", "country": "Malaysia",      "unit": "people", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "usa_population",             "country_code": "USA", "indicator_code": "SP.POP.TOTL", "country": "United States", "unit": "people", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "china_population",           "country_code": "CHN", "indicator_code": "SP.POP.TOTL", "country": "China",         "unit": "people", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_population",          "country_code": "WLD", "indicator_code": "SP.POP.TOTL", "country": "Global",        "unit": "people", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── HEALTH: Life Expectancy ──────────────────────────────────────────
    {"metric_key": "singapore_life_expectancy",  "country_code": "SGP", "indicator_code": "SP.DYN.LE00.IN", "country": "Singapore",     "unit": "years", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_life_expectancy",   "country_code": "MYS", "indicator_code": "SP.DYN.LE00.IN", "country": "Malaysia",      "unit": "years", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "usa_life_expectancy",        "country_code": "USA", "indicator_code": "SP.DYN.LE00.IN", "country": "United States", "unit": "years", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "china_life_expectancy",      "country_code": "CHN", "indicator_code": "SP.DYN.LE00.IN", "country": "China",         "unit": "years", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_life_expectancy",     "country_code": "WLD", "indicator_code": "SP.DYN.LE00.IN", "country": "Global",        "unit": "years", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── HEALTH: Infant Mortality (per 1000 live births) ──────────────────
    {"metric_key": "singapore_infant_mortality", "country_code": "SGP", "indicator_code": "SP.DYN.IMRT.IN", "country": "Singapore",     "unit": "per 1000", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_infant_mortality",  "country_code": "MYS", "indicator_code": "SP.DYN.IMRT.IN", "country": "Malaysia",      "unit": "per 1000", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_infant_mortality",    "country_code": "WLD", "indicator_code": "SP.DYN.IMRT.IN", "country": "Global",        "unit": "per 1000", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── HEALTH: Vaccination Rate (DPT, % of children under 12 months) ───
    {"metric_key": "singapore_vaccination_rate", "country_code": "SGP", "indicator_code": "SH.IMM.IDPT", "country": "Singapore", "unit": "%", "source_name": "World Bank / WHO", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_vaccination_rate",  "country_code": "MYS", "indicator_code": "SH.IMM.IDPT", "country": "Malaysia",  "unit": "%", "source_name": "World Bank / WHO", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_vaccination_rate",    "country_code": "WLD", "indicator_code": "SH.IMM.IDPT", "country": "Global",    "unit": "%", "source_name": "World Bank / WHO", "source_url": "https://data.worldbank.org/"},

    # ── EDUCATION: Literacy Rate ─────────────────────────────────────────
    {"metric_key": "singapore_literacy_rate",    "country_code": "SGP", "indicator_code": "SE.ADT.LITR.ZS", "country": "Singapore", "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_literacy_rate",     "country_code": "MYS", "indicator_code": "SE.ADT.LITR.ZS", "country": "Malaysia",  "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_literacy_rate",       "country_code": "WLD", "indicator_code": "SE.ADT.LITR.ZS", "country": "Global",    "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── ENVIRONMENT: CO2 Emissions (metric tons per capita) ──────────────
    {"metric_key": "singapore_co2_emissions",    "country_code": "SGP", "indicator_code": "EN.ATM.CO2E.PC", "country": "Singapore",     "unit": "metric tons", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_co2_emissions",     "country_code": "MYS", "indicator_code": "EN.ATM.CO2E.PC", "country": "Malaysia",      "unit": "metric tons", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "usa_co2_emissions",          "country_code": "USA", "indicator_code": "EN.ATM.CO2E.PC", "country": "United States", "unit": "metric tons", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "china_co2_emissions",        "country_code": "CHN", "indicator_code": "EN.ATM.CO2E.PC", "country": "China",         "unit": "metric tons", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_co2_emissions",       "country_code": "WLD", "indicator_code": "EN.ATM.CO2E.PC", "country": "Global",        "unit": "metric tons", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── POVERTY ──────────────────────────────────────────────────────────
    {"metric_key": "malaysia_poverty_rate",      "country_code": "MYS", "indicator_code": "SI.POV.DDAY", "country": "Malaysia", "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "global_poverty_rate",        "country_code": "WLD", "indicator_code": "SI.POV.DDAY", "country": "Global",   "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},

    # ── TRADE: Exports (% of GDP) ────────────────────────────────────────
    {"metric_key": "singapore_exports_gdp",      "country_code": "SGP", "indicator_code": "NE.EXP.GNFS.ZS", "country": "Singapore", "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
    {"metric_key": "malaysia_exports_gdp",       "country_code": "MYS", "indicator_code": "NE.EXP.GNFS.ZS", "country": "Malaysia",  "unit": "%", "source_name": "World Bank", "source_url": "https://data.worldbank.org/"},
]

def fetch_indicator(country_code, indicator_code):
    url = (
        f"https://api.worldbank.org/v2/country/{country_code}"
        f"/indicator/{indicator_code}?format=json&mrv=5"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return None, None
        for record in data[1]:
            value = record.get("value")
            year = record.get("date")
            if value is not None and year is not None:
                return float(value), int(year)
    except Exception as e:
        print(f"  ERR {indicator_code} / {country_code}: {e}")
    return None, None


def load_data():
    stat_entity = TrustedStatistic()
    print(f"Loading {len(SUPPORTED_INDICATORS)} indicators...\n")
    success, fail = 0, 0

    for ind in SUPPORTED_INDICATORS:
        print(f"Fetching {ind['metric_key']} ...")
        value, year = fetch_indicator(ind["country_code"], ind["indicator_code"])
        if value is not None and year is not None:
            value = round(value, 0) if ind["unit"] == "people" else round(value, 2)
            stat_entity.upsert_stat(        # ← uses entity now
                ind["metric_key"], ind["country"], year, value,
                ind["unit"], ind["source_name"], ind["source_url"]
            )
            success += 1
        else:
            print(f"  SKIP {ind['metric_key']} — no data returned")
            fail += 1

    print(f"\nDone. {success} updated, {fail} skipped.")


if __name__ == "__main__":
    load_data()