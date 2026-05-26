"""
filters.py — Data loading, cleaning, and filter logic for the Pakistan Dashboard.
"""
import os
import pandas as pd
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "gadm41_PAK_shp.csv")

# ── Load & cache ──────────────────────────────────────────────────────────────
_df_cache = None

def load_data() -> pd.DataFrame:
    global _df_cache
    if _df_cache is not None:
        return _df_cache
    df = pd.read_csv(DATA_PATH)
    df = clean_data(df)
    _df_cache = df
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Drop full duplicates
    df = df.drop_duplicates()
    # Clip impossible values
    df['Literacy_Rate']    = df['Literacy_Rate'].clip(0, 100)
    df['Female_Literacy']  = df['Female_Literacy'].clip(0, 100)
    df['Male_Literacy']    = df['Male_Literacy'].clip(0, 100)
    df['Poverty_Rate']     = df['Poverty_Rate'].clip(0, 100)
    df['Electricity_Access'] = df['Electricity_Access'].clip(0, 100)
    df['Water_Access']     = df['Water_Access'].clip(0, 100)
    df['Life_Expectancy']  = df['Life_Expectancy'].clip(30, 90)
    # Fill any NaNs with column median for numerics
    num_cols = df.select_dtypes(include='number').columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    return df

# ── Filter application ────────────────────────────────────────────────────────
def apply_filters(df: pd.DataFrame,
                  year_range: tuple = None,
                  provinces: list = None,
                  sectors: list = None,
                  urban_rural: list = None,
                  literacy_range: tuple = None,
                  gdp_range: tuple = None,
                  search_text: str = "") -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)

    if year_range:
        mask &= df['Year'].between(year_range[0], year_range[1])
    if provinces:
        mask &= df['Province'].isin(provinces)
    if sectors:
        mask &= df['Dominant_Sector'].isin(sectors)
    if urban_rural:
        mask &= df['Urban_Rural'].isin(urban_rural)
    if literacy_range:
        mask &= df['Literacy_Rate'].between(literacy_range[0], literacy_range[1])
    if gdp_range:
        mask &= df['GDP_Per_Capita'].between(gdp_range[0], gdp_range[1])
    if search_text:
        s = search_text.lower()
        mask &= (
            df['District'].str.lower().str.contains(s, na=False) |
            df['Division'].str.lower().str.contains(s, na=False) |
            df['Province'].str.lower().str.contains(s, na=False)
        )
    return df[mask].copy()

# ── KPI helpers ───────────────────────────────────────────────────────────────
def compute_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    latest = df[df['Year'] == df['Year'].max()]
    return {
        "total_records":    len(df),
        "total_population": int(latest['Population'].sum()),
        "avg_literacy":     round(df['Literacy_Rate'].mean(), 1),
        "avg_gdp":          round(df['GDP_Per_Capita'].mean(), 0),
        "avg_poverty":      round(df['Poverty_Rate'].mean(), 1),
        "avg_life_exp":     round(df['Life_Expectancy'].mean(), 1),
        "avg_electricity":  round(df['Electricity_Access'].mean(), 1),
        "districts":        df['District'].nunique(),
        "provinces":        df['Province'].nunique(),
    }
