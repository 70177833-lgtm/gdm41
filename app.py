"""
app.py — Pakistan Administrative Data Dashboard
A Power BI–style interactive dashboard built with Streamlit.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from filters import load_data, apply_filters, compute_kpis
import charts as ch

# ══════════════════════════════════════════════════════════════════════════════
# Page configuration
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Pakistan Districts Dashboard",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# Custom CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Background */
.stApp { background-color: #f0f2f6; }
section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 2px solid #e0e0e0; }
section[data-testid="stSidebar"] * { color: #1a1a2e !important; }

/* Main text */
html, body, [class*="css"] { color: #1a1a2e; font-family: 'Segoe UI', sans-serif; }

/* KPI Cards */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-top: 4px solid #1b4f72;
    border-radius: 6px;
    padding: 12px 14px;
    margin: 4px 0;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    overflow: hidden;
}
.kpi-card:hover { border-top-color: #2e86c1; box-shadow: 0 3px 12px rgba(0,0,0,0.12); }
.kpi-label {
    font-size: 10px;
    color: #7f8c8d;
    text-transform: uppercase;
    letter-spacing: 1px;
    white-space: nowrap;
}
.kpi-value {
    font-size: 22px;
    font-weight: 700;
    color: #1b4f72;
    margin: 4px 0 2px;
    white-space: nowrap;
}
.kpi-sub {
    font-size: 9px;
    color: #aab7b8;
    white-space: nowrap;
}

/* Tabs */
button[data-baseweb="tab"] { color: #7f8c8d !important; font-size: 13px; }
button[data-baseweb="tab"][aria-selected="true"] { color: #1b4f72 !important; border-bottom: 2px solid #1b4f72; }

/* Inputs */
.stMultiSelect span { background: #d6eaf8 !important; color: #1b4f72 !important; }

/* Divider */
hr { border-color: #e0e0e0; }

/* Header */
.dash-header {
    background: linear-gradient(90deg, #1b4f72 0%, #2e86c1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.dash-sub { color: #7f8c8d; font-size: 13px; margin-top: -6px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Load data
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def get_data():
    return load_data()

df_raw = get_data()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Filters
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🗂️ Filters")
    st.markdown("---")

    if st.button("🔄 Reset All Filters", use_container_width=True):
        for key in ["year_slider", "prov", "sector", "ur", "lit", "gdp", "search"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("### 📅 Year Range")
    yr_min, yr_max = int(df_raw['Year'].min()), int(df_raw['Year'].max())
    year_range = st.slider("Select Years", yr_min, yr_max, (yr_min, yr_max), key="year_slider")

    st.markdown("### 🗺️ Province")
    all_provinces = sorted(df_raw['Province'].unique())
    provinces = st.multiselect("Select Province(s)", all_provinces, default=all_provinces, key="prov")

    st.markdown("### 🏭 Dominant Sector")
    all_sectors = sorted(df_raw['Dominant_Sector'].unique())
    sectors = st.multiselect("Select Sector(s)", all_sectors, default=all_sectors, key="sector")

    st.markdown("### 🏘️ Urban / Rural")
    all_ur = sorted(df_raw['Urban_Rural'].unique())
    urban_rural = st.multiselect("Settlement Type", all_ur, default=all_ur, key="ur")

    st.markdown("### 📖 Literacy Range (%)")
    lit_min = float(df_raw['Literacy_Rate'].min())
    lit_max = float(df_raw['Literacy_Rate'].max())
    literacy_range = st.slider("Literacy Rate", lit_min, lit_max, (lit_min, lit_max), key="lit")

    st.markdown("### 💰 GDP Per Capita (PKR)")
    gdp_min = float(df_raw['GDP_Per_Capita'].min())
    gdp_max = float(df_raw['GDP_Per_Capita'].max())
    gdp_range = st.slider("GDP Range", gdp_min, gdp_max, (gdp_min, gdp_max), key="gdp", format="%.0f")

    st.markdown("### 🔍 Search")
    search_text = st.text_input("Search by District / Division / Province", key="search")

    st.markdown("---")
    st.markdown(f"<small style='color:#7f8c8d'>Dataset: gadm41_PAK_shp.csv<br>Records: {len(df_raw):,}</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Apply filters
# ══════════════════════════════════════════════════════════════════════════════
df = apply_filters(
    df_raw,
    year_range=year_range,
    provinces=provinces if provinces else None,
    sectors=sectors if sectors else None,
    urban_rural=urban_rural if urban_rural else None,
    literacy_range=literacy_range,
    gdp_range=gdp_range,
    search_text=search_text,
)

kpis = compute_kpis(df)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="dash-header">🇵🇰 Pakistan Districts Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="dash-sub">Exploratory Data Analysis · Administrative & Socioeconomic Indicators · 2015–2024</p>', unsafe_allow_html=True)
st.markdown("---")

if df.empty:
    st.warning("⚠️ No records match the current filters. Please adjust the sidebar filters.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS — 2 rows of 4
# ══════════════════════════════════════════════════════════════════════════════
def kpi_card(col, label, value, sub=""):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
kpi_card(k1, "Total Records",   f"{kpis.get('total_records',0):,}",         "filtered rows")
kpi_card(k2, "Districts",       f"{kpis.get('districts',0)}",                "unique districts")
kpi_card(k3, "Provinces",       f"{kpis.get('provinces',0)}",                "selected")
kpi_card(k4, "Population",      f"{kpis.get('total_population',0)/1e6:.1f}M","latest year total")

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

k5, k6, k7, k8 = st.columns(4)
kpi_card(k5, "Avg Literacy",    f"{kpis.get('avg_literacy',0):.1f}%",        "literacy rate")
kpi_card(k6, "Avg GDP/Capita",  f"Rs {kpis.get('avg_gdp',0):,.0f}",         "PKR per capita")
kpi_card(k7, "Life Expectancy", f"{kpis.get('avg_life_exp',0):.1f} yrs",     "average years")
kpi_card(k8, "Electricity",     f"{kpis.get('avg_electricity',0):.1f}%",     "access rate")

st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Overview",
    "📈 Trends",
    "🌍 Demographics",
    "💡 Development",
    "🔬 Advanced Analytics",
    "📋 Data Table",
])

# ── TAB 1: Overview ──────────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Overview — Population & Sector Distribution")
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        st.pyplot(ch.chart_pie_province_population(df), use_container_width=True)
        st.caption("📌 Punjab dominates with ~50% of total population, followed by Sindh and KPK.")
    with r1c2:
        st.pyplot(ch.chart_count_sector(df), use_container_width=True)
        st.caption("📌 Records are fairly distributed across all economic sectors in the dataset.")
    with r1c3:
        st.pyplot(ch.chart_funnel_urban_rural(df), use_container_width=True)
        st.caption("📌 Rural areas hold the largest share of population across Pakistan's districts.")

    st.markdown("---")
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.pyplot(ch.chart_bar_literacy_province(df), use_container_width=True)
        st.caption("📌 Islamabad leads in literacy while Balochistan and FATA have the lowest rates.")
    with r2c2:
        st.pyplot(ch.chart_histogram_literacy(df), use_container_width=True)
        st.caption("📌 Literacy rates are normally distributed with most districts falling between 50–70%.")

# ── TAB 2: Trends ────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Temporal Trends — GDP, Population & Literacy")
    st.pyplot(ch.chart_line_gdp_trend(df), use_container_width=True)
    st.caption("📌 GDP per capita has grown steadily across all provinces from 2015 to 2024, with Islamabad consistently the highest.")
    st.markdown("---")
    st.pyplot(ch.chart_area_population(df), use_container_width=True)
    st.caption("📌 Total population has increased every year. Punjab contributes the largest and fastest-growing share.")

    st.markdown("#### Year-on-Year Summary")
    yr_tbl = df.groupby('Year').agg(
        Avg_GDP=('GDP_Per_Capita','mean'),
        Avg_Literacy=('Literacy_Rate','mean'),
        Avg_Poverty=('Poverty_Rate','mean'),
        Total_Pop=('Population','sum'),
    ).round(1)
    yr_tbl['Total_Pop'] = yr_tbl['Total_Pop'].apply(lambda x: f"{x/1e6:.1f}M")
    yr_tbl['Avg_GDP']   = yr_tbl['Avg_GDP'].apply(lambda x: f"Rs {x:,.0f}")
    st.dataframe(yr_tbl, use_container_width=True)
    st.caption("📌 National averages show consistent improvement in GDP and literacy, with poverty declining year over year.")

# ── TAB 3: Demographics ──────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("Demographics — Literacy, Poverty & Life Expectancy")
    dc1, dc2 = st.columns(2)
    with dc1:
        st.pyplot(ch.chart_box_poverty(df), use_container_width=True)
        st.caption("📌 Balochistan and FATA show the highest and most spread out poverty rates. Islamabad has the lowest.")
    with dc2:
        st.pyplot(ch.chart_violin_life_expectancy(df), use_container_width=True)
        st.caption("📌 Life expectancy is highest in Islamabad and Gilgit-Baltistan, lowest in Balochistan.")

    st.markdown("---")
    st.pyplot(ch.chart_scatter_gdp_literacy(df), use_container_width=True)
    st.caption("📌 Strong positive trend — districts with higher literacy rates consistently show higher GDP per capita.")

    st.markdown("#### Gender Literacy Gap by Province")
    gap = df.groupby('Province').agg(
        Male=('Male_Literacy','mean'),
        Female=('Female_Literacy','mean'),
    ).round(1)
    gap['Gap'] = (gap['Male'] - gap['Female']).round(1)
    gap = gap.sort_values('Gap', ascending=False)
    st.dataframe(gap.style.background_gradient(subset=['Gap'], cmap='RdYlGn_r'), use_container_width=True)
    st.caption("📌 Balochistan has the largest gender literacy gap — male literacy is over 20 points higher than female.")

# ── TAB 4: Development ───────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("Development Indicators — Infrastructure & Health")
    dv1, dv2 = st.columns(2)

    with dv1:
        fig, ax = plt.subplots(figsize=(5.5, 3.8))
        agg = df.groupby('Province')[['Electricity_Access','Water_Access']].mean()
        x = range(len(agg))
        ax.bar([i-0.2 for i in x], agg['Electricity_Access'], width=0.38,
               label='Electricity', color='#1b4f72', edgecolor='#f0f2f6', alpha=0.85)
        ax.bar([i+0.2 for i in x], agg['Water_Access'], width=0.38,
               label='Water', color='#148f77', edgecolor='#f0f2f6', alpha=0.85)
        ax.set_xticks(list(x))
        ax.set_xticklabels(agg.index, rotation=30, ha='right', fontsize=7, color='#1a1a2e')
        ax.set_ylabel('Access (%)', color='#1a1a2e')
        ax.tick_params(colors='#1a1a2e')
        ax.legend(fontsize=8, facecolor='#f8f9fa', labelcolor='#1a1a2e')
        ax.set_facecolor('#f8f9fa'); fig.patch.set_facecolor('#f8f9fa')
        ax.set_title('Electricity & Water Access by Province', color='#1a1a2e', fontsize=10)
        for spine in ax.spines.values(): spine.set_edgecolor('#e0e0e0')
        ax.grid(color='#e0e0e0', linewidth=0.5, alpha=0.6)
        st.pyplot(fig, use_container_width=True)
        st.caption("📌 Islamabad and Punjab have the best infrastructure access. Balochistan lags behind in both electricity and water.")

    with dv2:
        fig2, ax2 = plt.subplots(figsize=(5.5, 3.8))
        im = df.groupby('Province')['Infant_Mortality_per1000'].mean().sort_values()
        ax2.barh(im.index, im.values,
                 color=['#c0392b' if v > im.median() else '#148f77' for v in im.values],
                 edgecolor='#f0f2f6', alpha=0.85)
        ax2.axvline(im.median(), color='#1a1a2e', linestyle='--', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Infant Mortality (per 1000)', color='#1a1a2e')
        ax2.tick_params(colors='#1a1a2e', labelsize=8)
        ax2.set_facecolor('#f8f9fa'); fig2.patch.set_facecolor('#f8f9fa')
        ax2.set_title('Infant Mortality by Province', color='#1a1a2e', fontsize=10)
        for spine in ax2.spines.values(): spine.set_edgecolor('#e0e0e0')
        ax2.grid(color='#e0e0e0', linewidth=0.5, alpha=0.6)
        st.pyplot(fig2, use_container_width=True)
        st.caption("📌 Red bars exceed the national median. Balochistan and FATA have critically high infant mortality rates.")

    st.markdown("---")
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    sample = df.sample(min(500, len(df)), random_state=7)
    provinces_list = sample['Province'].unique()
    PALETTE = ["#1b4f72","#2e86c1","#148f77","#d35400","#7d3c98","#1a5276","#117a65","#b7950b"]
    for i, p in enumerate(provinces_list):
        sub = sample[sample['Province']==p]
        ax3.scatter(sub['Health_Expenditure_PKR'], sub['Education_Expenditure_PKR'],
                    color=PALETTE[i%len(PALETTE)], alpha=0.6, s=20, label=p)
    ax3.set_xlabel('Health Expenditure (PKR)', color='#1a1a2e')
    ax3.set_ylabel('Education Expenditure (PKR)', color='#1a1a2e')
    ax3.tick_params(colors='#1a1a2e', labelsize=7)
    ax3.legend(fontsize=7, facecolor='#f8f9fa', labelcolor='#1a1a2e', ncol=2)
    ax3.set_facecolor('#f8f9fa'); fig3.patch.set_facecolor('#f8f9fa')
    ax3.set_title('Health vs Education Expenditure', color='#1a1a2e', fontsize=10)
    for spine in ax3.spines.values(): spine.set_edgecolor('#e0e0e0')
    ax3.grid(color='#e0e0e0', linewidth=0.5, alpha=0.6)
    st.pyplot(fig3, use_container_width=True)
    st.caption("📌 Health and education spending are positively correlated — provinces that invest more in one tend to invest more in the other.")

# ── TAB 5: Advanced Analytics ────────────────────────────────────────────────
with tabs[4]:
    st.subheader("Advanced Analytics")
    aa1, aa2 = st.columns(2)
    with aa1:
        st.pyplot(ch.chart_heatmap_correlation(df), use_container_width=True)
        st.caption("📌 Literacy strongly correlates with GDP and life expectancy, and negatively with poverty and infant mortality.")
    with aa2:
        st.pyplot(ch.chart_bubble_literacy_poverty(df), use_container_width=True)
        st.caption("📌 Larger bubbles mean larger population. Punjab is both large and relatively more literate than Balochistan.")

    st.markdown("---")
    st.markdown("#### Pair Plot — Key Indicators")
    with st.spinner("Rendering pair plot..."):
        st.pyplot(ch.chart_pairplot(df), use_container_width=True)
    st.caption("📌 Each province forms distinct clusters — Islamabad separates clearly from others in GDP and literacy dimensions.")

    st.markdown("---")
    st.markdown("#### Statistical Summary")
    num_cols = ['Literacy_Rate','Male_Literacy','Female_Literacy',
                'GDP_Per_Capita','Poverty_Rate','Unemployment_Rate',
                'Electricity_Access','Water_Access','Life_Expectancy',
                'Infant_Mortality_per1000','Crime_Rate_per100k']
    st.dataframe(df[num_cols].describe().round(2), use_container_width=True)
    st.caption("📌 Summary statistics for all key numerical indicators after applying current filters.")

# ── TAB 6: Data Table ────────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("Raw Data Explorer")
    cols_show = st.multiselect(
        "Select columns to display",
        options=list(df.columns),
        default=['Year','Province','Division','District','Urban_Rural','Population',
                 'Literacy_Rate','GDP_Per_Capita','Poverty_Rate','Life_Expectancy'],
    )
    sort_col = st.selectbox("Sort by", options=cols_show, index=0)
    sort_asc = st.radio("Order", ["Ascending","Descending"], horizontal=True) == "Ascending"
    disp = df[cols_show].sort_values(sort_col, ascending=sort_asc)
    st.dataframe(disp, use_container_width=True, height=420)
    st.caption(f"📌 Showing {len(disp):,} records after applying all active filters. You can download the filtered data below.")
    csv = disp.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Filtered CSV", csv, "pak_filtered_data.csv", "text/csv", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# Footer
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<p style='text-align:center;color:#aab7b8;font-size:11px;margin-top:10px;'>"
    "Pakistan Districts Dashboard · EDA Project · Dataset: gadm41_PAK_shp · "
    "Built with Streamlit, Pandas, Matplotlib, Seaborn"
    "</p>", unsafe_allow_html=True
)
