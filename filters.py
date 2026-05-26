"""
filters.py — Data loading, cleaning, and filter logic for the Pakistan Dashboard.
"""
import os
import struct
import zipfile
import io
import random
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

BASE_DIR  = os.path.dirname(__file__)
DATA_DIR  = BASE_DIR
CSV_PATH  = os.path.join(BASE_DIR, "gadm41_PAK_shp.csv")
ZIP_PATH  = os.path.join(BASE_DIR, "gadm41_PAK_shp.zip")

def _read_dbf_raw(zf, filename):
    with zf.open(filename) as f:
        raw = f.read()
    buf = io.BytesIO(raw)
    buf.read(4)
    num_records = struct.unpack('<I', buf.read(4))[0]
    header_size = struct.unpack('<H', buf.read(2))[0]
    buf.seek(32)
    fields = []
    while True:
        fd = buf.read(32)
        if not fd or fd[0] == 0x0D:
            break
        name = fd[:11].decode('latin-1').rstrip('\x00')
        fields.append((name, chr(fd[11]), fd[16]))
    buf.seek(header_size)
    records = []
    for _ in range(num_records):
        buf.read(1)
        row = {n: buf.read(l).decode('latin-1').strip() for n, t, l in fields}
        records.append(row)
    return pd.DataFrame(records)

def _generate_csv():
    province_cfg = {
        'Azad Kashmir':       {'pop': 4_500_000,  'gdp': 38000, 'lit': 72, 'rain': 1000},
        'Balochistan':        {'pop': 12_000_000, 'gdp': 32000, 'lit': 45, 'rain': 180},
        'Federally Administered Tribal Ar': {'pop': 5_000_000, 'gdp': 28000, 'lit': 42, 'rain': 400},
        'Gilgit-Baltistan':   {'pop': 1_800_000,  'gdp': 28000, 'lit': 72, 'rain': 250},
        'Islamabad':          {'pop': 2_200_000,  'gdp': 150000,'lit': 88, 'rain': 900},
        'Khyber-Pakhtunkhwa': {'pop': 35_000_000, 'gdp': 40000, 'lit': 54, 'rain': 500},
        'Punjab':             {'pop': 110_000_000,'gdp': 85000, 'lit': 62, 'rain': 400},
        'Sindh':              {'pop': 48_000_000, 'gdp': 75000, 'lit': 58, 'rain': 200},
    }
    YEARS   = list(range(2015, 2025))
    SECTORS = ['Agriculture','Manufacturing','Services','Construction','Mining','Education','Healthcare']
    UR_CATS = ['Urban','Rural','Semi-Urban']

    with zipfile.ZipFile(ZIP_PATH) as zf:
        df3 = _read_dbf_raw(zf, "gadm41_PAK_3.dbf")

    rows = []
    for _, drow in df3.iterrows():
        prov = drow['NAME_1']
        div  = drow['NAME_2']
        dist = drow['NAME_3']
        cfg  = province_cfg.get(prov, {'pop': 5_000_000, 'gdp': 35000, 'lit': 50, 'rain': 300})
        n    = len(df3[df3['NAME_1'] == prov])
        base_pop = max(100_000, int(cfg['pop'] / n * random.uniform(0.4, 2.2)))

        for year in YEARS:
            g   = 1 + random.uniform(0.01, 0.035)
            pop = int(base_pop * (g ** (year - 2015)))
            lit = float(np.clip(cfg['lit'] + np.random.normal(0, 5) + (year-2015)*0.4, 10, 98))
            gdp = cfg['gdp'] * random.uniform(0.6, 1.4) * (1.03 ** (year-2015))
            pov = float(np.clip(60 - lit*0.5 + np.random.normal(0,4), 2, 80))
            unemp = float(np.clip(12 - (lit-50)*0.1 + np.random.normal(0,2), 1, 35))
            area  = random.uniform(500, 8000) if 'Balo' not in prov else random.uniform(2000,30000)
            schools = max(1, int(pop / random.uniform(2000, 5000)))
            hospitals = max(1, int(pop / random.uniform(40000, 100000)))
            elec  = float(np.clip(lit*0.9 + random.uniform(0,15), 10, 100))
            water = float(np.clip(lit*0.85 + random.uniform(0,20), 10, 100))
            rain  = cfg['rain'] * random.uniform(0.5, 1.5)
            temp  = random.uniform(5,18) if 'Gilgit' in prov else random.uniform(18,32)
            crime = float(np.clip(50 - lit*0.4 + np.random.normal(0,8), 0, 100))
            f_lit = float(np.clip(lit - random.uniform(5,20), 5, 98))
            m_lit = float(np.clip(lit + random.uniform(2,12), 10, 100))
            inf_m = float(np.clip(80 - lit*0.6 + np.random.normal(0,5), 5, 120))
            life  = float(np.clip(45 + lit*0.3 + np.random.normal(0,2), 40, 82))
            agri  = random.uniform(20,70) if 'Balo' in prov else random.uniform(10,55)

            rows.append({
                'Year': year, 'Province': prov, 'Division': div, 'District': dist,
                'Admin_Type': drow['ENGTYPE_3'],
                'Urban_Rural': np.random.choice(UR_CATS, p=[0.35,0.45,0.20]),
                'Dominant_Sector': random.choice(SECTORS),
                'Population': pop, 'Population_Density': round(pop/area, 2),
                'Area_km2': round(area, 1), 'Literacy_Rate': round(lit, 2),
                'Male_Literacy': round(m_lit, 2), 'Female_Literacy': round(f_lit, 2),
                'GDP_Per_Capita': round(gdp, 0), 'Poverty_Rate': round(pov, 2),
                'Unemployment_Rate': round(unemp, 2), 'Num_Schools': schools,
                'Num_Hospitals': hospitals, 'Electricity_Access': round(elec, 2),
                'Water_Access': round(water, 2), 'Road_Network_km': int(area * random.uniform(0.3, 1.2)),
                'Annual_Rainfall_mm': round(rain, 1), 'Avg_Temperature_C': round(temp, 1),
                'Crime_Rate_per100k': round(crime, 2),
                'Health_Expenditure_PKR': round(gdp * random.uniform(0.02, 0.05), 0),
                'Education_Expenditure_PKR': round(gdp * random.uniform(0.03, 0.07), 0),
                'Agriculture_Share_pct': round(agri, 2),
                'Infant_Mortality_per1000': round(inf_m, 2), 'Life_Expectancy': round(life, 2),
            })

    df = pd.DataFrame(rows)
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    return df

# ── Load & cache ──────────────────────────────────────────────────────────────
_df_cache = None

def load_data() -> pd.DataFrame:
    global _df_cache
    if _df_cache is not None:
        return _df_cache
    if not os.path.exists(CSV_PATH):
        df = _generate_csv()
    else:
        df = pd.read_csv(CSV_PATH)
    df = clean_data(df)
    _df_cache = df
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    df['Literacy_Rate']      = df['Literacy_Rate'].clip(0, 100)
    df['Female_Literacy']    = df['Female_Literacy'].clip(0, 100)
    df['Male_Literacy']      = df['Male_Literacy'].clip(0, 100)
    df['Poverty_Rate']       = df['Poverty_Rate'].clip(0, 100)
    df['Electricity_Access'] = df['Electricity_Access'].clip(0, 100)
    df['Water_Access']       = df['Water_Access'].clip(0, 100)
    df['Life_Expectancy']    = df['Life_Expectancy'].clip(30, 90)
    num_cols = df.select_dtypes(include='number').columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    return df

# ── Filter application ────────────────────────────────────────────────────────
def apply_filters(df, year_range=None, provinces=None, sectors=None,
                  urban_rural=None, literacy_range=None, gdp_range=None,
                  search_text=""):
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
def compute_kpis(df) -> dict:
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
