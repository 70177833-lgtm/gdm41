# 🇵🇰 Pakistan Districts Analytics Dashboard

A **Power BI–style** interactive data visualization dashboard built with Streamlit, Pandas, Matplotlib, and Seaborn. Analyzes Pakistan's administrative and socioeconomic data across 8 provinces, 141 districts, and 10 years (2015–2024).

---

## 📁 Project Structure

```
dashboard_project/
├── data/
│   ├── gadm41_PAK_shp.zip     ← Original dataset (DO NOT RENAME)
│   └── gadm41_PAK_shp.csv     ← Generated enriched CSV
├── notebooks/
│   └── analysis.ipynb         ← EDA notebook
├── app.py                     ← Main Streamlit dashboard
├── charts.py                  ← All visualization functions
├── filters.py                 ← Data loading, cleaning & filtering
├── generate_data.py           ← One-time CSV generation script
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate the dataset (run ONCE)

```bash
python generate_data.py
```

This reads `gadm41_PAK_shp.zip` and creates `data/gadm41_PAK_shp.csv`.

### 3. Launch the dashboard

```bash
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

---

## 📊 Dashboard Features

### KPI Summary Cards (8 metrics)
- Total records, Districts, Provinces, Population, Avg Literacy, Avg GDP/Capita, Life Expectancy, Electricity Access

### Sidebar Filters (all linked to all charts)
| Filter | Type |
|---|---|
| Year Range | Slider |
| Province | Multi-select |
| Dominant Sector | Multi-select |
| Urban/Rural/Semi-Urban | Multi-select |
| Literacy Rate | Range slider |
| GDP Per Capita | Range slider |
| Search (District/Division/Province) | Text input |
| Reset All Filters | Button |

### 5 Dashboard Tabs + 1 Data Explorer

| Tab | Contents |
|---|---|
| 📊 Overview | Pie, Count, Funnel, Bar, Histogram |
| 📈 Trends | Line chart (GDP), Area chart (Population), Year-on-year table |
| 🌍 Demographics | Box plot, Violin, Scatter (GDP vs Literacy), Gender gap table |
| 💡 Development | Grouped bar (Electricity/Water), Infant mortality, Expenditure scatter |
| 🔬 Advanced | Correlation heatmap, Bubble chart, Pair plot, Stats summary |
| 📋 Data Table | Sortable, column-selectable, CSV download |

### Chart Types Included (10 required + 3 bonus)
1. ✅ Pie Chart
2. ✅ Histogram
3. ✅ Line Chart
4. ✅ Bar Chart (horizontal + grouped)
5. ✅ Scatter Plot
6. ✅ Box Plot
7. ✅ Heatmap (correlation matrix)
8. ✅ Area Chart (stacked)
9. ✅ Count Plot
10. ✅ Violin Plot
11. 🌟 Bubble Chart (bonus)
12. 🌟 Pair Plot (bonus)
13. 🌟 Funnel Chart (bonus)

---

## 📋 Dataset

**File:** `gadm41_PAK_shp.zip` → `gadm41_PAK_shp.csv`

**Source:** GADM (Global Administrative Areas) Pakistan Level 3 + synthetic socioeconomic indicators

**Features (29 columns):**
- Geographic: Province, Division, District, Area_km2, Population_Density
- Social: Literacy_Rate, Male_Literacy, Female_Literacy, Infant_Mortality, Life_Expectancy
- Economic: GDP_Per_Capita, Poverty_Rate, Unemployment_Rate, Agriculture_Share_pct
- Infrastructure: Electricity_Access, Water_Access, Road_Network_km, Num_Schools, Num_Hospitals
- Environment: Annual_Rainfall_mm, Avg_Temperature_C
- Safety: Crime_Rate_per100k
- Expenditure: Health_Expenditure_PKR, Education_Expenditure_PKR

---

## 💡 Key Insights

- **Punjab** dominates population share (~58% of total)
- **Islamabad** has the highest GDP per capita (~3× national average)
- **Balochistan** shows widest gender literacy gap (>20 percentage points)
- Strong **negative correlation** between literacy and poverty rate (r ≈ −0.85)
- **Electricity access** strongly predicts GDP per capita (r ≈ 0.78)
- GDP per capita has grown steadily across all provinces 2015–2024

---

## 🛠️ Tech Stack

| Tool | Role |
|---|---|
| Python 3.x | Core language |
| Pandas | Data loading, cleaning, filtering, aggregation |
| NumPy | Numerical operations |
| Matplotlib | Core charts |
| Seaborn | Statistical visualizations (heatmap, pairplot) |
| Streamlit | Interactive dashboard frontend |

**Instructor:** Ali Hassan Sherazi | **Course:** Exploratory Data Analysis | **Submission:** 05-June-2026
