"""
charts.py — All chart/visualization functions for the Pakistan Dashboard.
Each function returns a matplotlib Figure.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np

# ── Palette & style ───────────────────────────────────────────────────────────
PALETTE   = ["#e94560","#f5a623","#00b4d8","#4cc9f0","#7209b7","#3a86ff","#06d6a0","#ffd166"]
BG_DARK   = "#1a1a2e"
BG_CARD   = "#16213e"
TEXT_CLR  = "#e0e0e0"
GRID_CLR  = "#0f3460"
ACCENT    = "#e94560"

def _style(fig, ax_list=None):
    fig.patch.set_facecolor(BG_CARD)
    if ax_list is None:
        ax_list = fig.axes
    for ax in ax_list:
        ax.set_facecolor(BG_CARD)
        ax.tick_params(colors=TEXT_CLR, labelsize=8)
        ax.xaxis.label.set_color(TEXT_CLR)
        ax.yaxis.label.set_color(TEXT_CLR)
        ax.title.set_color(TEXT_CLR)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_CLR)
        ax.grid(color=GRID_CLR, linewidth=0.5, alpha=0.6)


# 1 ── Pie Chart: Province population share ───────────────────────────────────
def chart_pie_province_population(df: pd.DataFrame) -> plt.Figure:
    data = df.groupby('Province')['Population'].sum().sort_values(ascending=False)
    total = data.sum()

    def autopct_filter(pct):
        return f'{pct:.1f}%' if pct > 4 else ''

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    wedges, texts, autotexts = ax.pie(
        data.values,
        labels=None,
        autopct=autopct_filter,
        startangle=140,
        colors=PALETTE[:len(data)],
        pctdistance=0.78,
        wedgeprops=dict(linewidth=1.5, edgecolor=BG_DARK),
        radius=0.85,
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(8)
        at.set_fontweight('bold')

    labels_pct = [f"{name}  ({val/total*100:.1f}%)" for name, val in zip(data.index, data.values)]
    ax.legend(wedges, labels_pct,
              loc='center left', bbox_to_anchor=(0.95, 0.5),
              fontsize=7, facecolor=BG_CARD, labelcolor=TEXT_CLR,
              framealpha=0.8, borderpad=0.8)

    ax.set_title("Population Share by Province", color=TEXT_CLR, fontsize=10, pad=8)
    fig.patch.set_facecolor(BG_CARD)
    fig.tight_layout()
    return fig


# 2 ── Histogram: Literacy Rate distribution ──────────────────────────────────
def chart_histogram_literacy(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.hist(df['Literacy_Rate'].dropna(), bins=25, color=ACCENT,
            edgecolor=BG_DARK, alpha=0.85)
    ax.set_xlabel("Literacy Rate (%)")
    ax.set_ylabel("Frequency")
    ax.set_title("Literacy Rate Distribution", color=TEXT_CLR, fontsize=10)
    _style(fig, [ax])
    return fig


# 3 ── Line Chart: Avg GDP per Capita over years ──────────────────────────────
def chart_line_gdp_trend(df: pd.DataFrame) -> plt.Figure:
    data = df.groupby(['Year', 'Province'])['GDP_Per_Capita'].mean().reset_index()
    provinces = data['Province'].unique()
    fig, ax = plt.subplots(figsize=(6, 3.8))
    for i, prov in enumerate(provinces):
        sub = data[data['Province'] == prov]
        ax.plot(sub['Year'], sub['GDP_Per_Capita'],
                marker='o', markersize=3, linewidth=1.8,
                color=PALETTE[i % len(PALETTE)], label=prov)
    ax.set_xlabel("Year"); ax.set_ylabel("GDP Per Capita (PKR)")
    ax.set_title("GDP Per Capita Trend by Province", color=TEXT_CLR, fontsize=10)
    ax.legend(fontsize=6, facecolor=BG_CARD, labelcolor=TEXT_CLR,
              loc='upper left', ncol=2, framealpha=0.7)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    _style(fig, [ax])
    return fig


# 4 ── Bar Chart: Avg Literacy by Province ───────────────────────────────────
def chart_bar_literacy_province(df: pd.DataFrame) -> plt.Figure:
    data = df.groupby('Province')['Literacy_Rate'].mean().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    bars = ax.barh(data.index, data.values,
                   color=[PALETTE[i % len(PALETTE)] for i in range(len(data))],
                   edgecolor=BG_DARK, linewidth=0.5)
    for bar, val in zip(bars, data.values):
        ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=7, color=TEXT_CLR)
    ax.set_xlabel("Avg Literacy Rate (%)")
    ax.set_title("Average Literacy Rate by Province", color=TEXT_CLR, fontsize=10)
    _style(fig, [ax])
    return fig


# 5 ── Scatter Plot: GDP vs Literacy ─────────────────────────────────────────
def chart_scatter_gdp_literacy(df: pd.DataFrame) -> plt.Figure:
    sample = df.sample(min(600, len(df)), random_state=1)
    provinces = sample['Province'].unique()
    cmap = {p: PALETTE[i % len(PALETTE)] for i, p in enumerate(provinces)}
    fig, ax = plt.subplots(figsize=(5.5, 4))
    for prov in provinces:
        sub = sample[sample['Province'] == prov]
        ax.scatter(sub['Literacy_Rate'], sub['GDP_Per_Capita'],
                   c=cmap[prov], alpha=0.55, s=15, label=prov)
    x, y = sample['Literacy_Rate'].dropna(), sample['GDP_Per_Capita'].dropna()
    idx = x.index.intersection(y.index)
    m, b = np.polyfit(x[idx], y[idx], 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, m*xs+b, color='white', linewidth=1.2, linestyle='--', alpha=0.5)
    ax.set_xlabel("Literacy Rate (%)"); ax.set_ylabel("GDP Per Capita (PKR)")
    ax.set_title("GDP vs Literacy Rate", color=TEXT_CLR, fontsize=10)
    ax.legend(fontsize=6, facecolor=BG_CARD, labelcolor=TEXT_CLR,
              ncol=2, framealpha=0.7, markerscale=1.5)
    _style(fig, [ax])
    return fig


# 6 ── Box Plot: Poverty Rate by Province ────────────────────────────────────
def chart_box_poverty(df: pd.DataFrame) -> plt.Figure:
    provinces = df['Province'].unique()
    fig, ax = plt.subplots(figsize=(6, 4))
    data_list = [df[df['Province'] == p]['Poverty_Rate'].dropna().values for p in provinces]
    bp = ax.boxplot(data_list, patch_artist=True, notch=False,
                    medianprops=dict(color='white', linewidth=1.5))
    for patch, color in zip(bp['boxes'], PALETTE):
        patch.set_facecolor(color); patch.set_alpha(0.75)
    for elem in ['whiskers', 'fliers', 'caps']:
        for item in bp[elem]:
            item.set(color=TEXT_CLR, linewidth=0.8)
    ax.set_xticks(range(1, len(provinces)+1))
    ax.set_xticklabels(provinces, rotation=20, ha='right', fontsize=7)
    ax.set_ylabel("Poverty Rate (%)")
    ax.set_title("Poverty Rate Distribution by Province", color=TEXT_CLR, fontsize=10)
    _style(fig, [ax])
    return fig


# 7 ── Heatmap: Correlation matrix ───────────────────────────────────────────
def chart_heatmap_correlation(df: pd.DataFrame) -> plt.Figure:
    cols = ['Literacy_Rate','GDP_Per_Capita','Poverty_Rate','Unemployment_Rate',
            'Electricity_Access','Water_Access','Life_Expectancy',
            'Infant_Mortality_per1000','Crime_Rate_per100k']
    corr = df[cols].corr()
    short = ['Literacy','GDP/Cap','Poverty','Unemp.','Electr.','Water','LifeExp','InfMort','Crime']
    corr.index = corr.columns = short
    fig, ax = plt.subplots(figsize=(6.5, 5))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, ax=ax, mask=mask, annot=True, fmt='.2f', linewidths=0.4,
                cmap='coolwarm', vmin=-1, vmax=1,
                annot_kws={'size': 7, 'color': 'white'},
                cbar_kws={'shrink': 0.8})
    ax.set_title("Feature Correlation Matrix", color=TEXT_CLR, fontsize=10, pad=8)
    ax.tick_params(colors=TEXT_CLR, labelsize=7)
    fig.patch.set_facecolor(BG_CARD)
    ax.set_facecolor(BG_CARD)
    ax.figure.axes[-1].tick_params(colors=TEXT_CLR, labelsize=7)
    return fig


# 8 ── Area Chart: Total population over years ────────────────────────────────
def chart_area_population(df: pd.DataFrame) -> plt.Figure:
    data = df.groupby(['Year', 'Province'])['Population'].sum().reset_index()
    pivoted = data.pivot(index='Year', columns='Province', values='Population').fillna(0)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    pivoted.plot.area(ax=ax, alpha=0.75, color=PALETTE[:len(pivoted.columns)], linewidth=0)
    ax.set_xlabel("Year"); ax.set_ylabel("Total Population")
    ax.set_title("Population Trend by Province (Stacked Area)", color=TEXT_CLR, fontsize=10)
    ax.legend(fontsize=6, facecolor=BG_CARD, labelcolor=TEXT_CLR,
              loc='upper left', ncol=2, framealpha=0.7)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v/1e6:.1f}M'))
    _style(fig, [ax])
    return fig


# 9 ── Count Plot: Districts per Sector ──────────────────────────────────────
def chart_count_sector(df: pd.DataFrame) -> plt.Figure:
    data = df['Dominant_Sector'].value_counts()
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    x_pos = range(len(data))
    bars = ax.bar(x_pos, data.values,
                  color=PALETTE[:len(data)], edgecolor=BG_DARK, linewidth=0.5)
    for bar, val in zip(bars, data.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(val), ha='center', fontsize=7, color=TEXT_CLR)
    ax.set_xlabel("Sector"); ax.set_ylabel("Count")
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(list(data.index), rotation=25, ha='right', fontsize=7)
    ax.set_title("Record Count by Dominant Sector", color=TEXT_CLR, fontsize=10)
    _style(fig, [ax])
    return fig


# 10 ── Violin Plot: Life Expectancy by Province ──────────────────────────────
def chart_violin_life_expectancy(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    provinces = df['Province'].unique()
    data_list = [df[df['Province']==p]['Life_Expectancy'].dropna().values for p in provinces]
    parts = ax.violinplot(data_list, showmedians=True, showextrema=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(PALETTE[i % len(PALETTE)])
        pc.set_alpha(0.75)
    parts['cmedians'].set_edgecolor('white')
    parts['cbars'].set_edgecolor(GRID_CLR)
    parts['cmins'].set_edgecolor(GRID_CLR)
    parts['cmaxes'].set_edgecolor(GRID_CLR)
    ax.set_xticks(range(1, len(provinces)+1))
    ax.set_xticklabels(provinces, rotation=20, ha='right', fontsize=7)
    ax.set_ylabel("Life Expectancy (years)")
    ax.set_title("Life Expectancy Distribution by Province", color=TEXT_CLR, fontsize=10)
    _style(fig, [ax])
    return fig


# BONUS ── Bubble Chart: Literacy vs Poverty (bubble = population) ────────────
def chart_bubble_literacy_poverty(df: pd.DataFrame) -> plt.Figure:
    agg = df.groupby('Province').agg(
        Literacy=('Literacy_Rate','mean'),
        Poverty=('Poverty_Rate','mean'),
        Population=('Population','sum')
    ).reset_index()
    sizes = (agg['Population'] / agg['Population'].max()) * 1500 + 100
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for i, row in agg.iterrows():
        ax.scatter(row['Literacy'], row['Poverty'], s=sizes[i],
                   color=PALETTE[i % len(PALETTE)], alpha=0.7, edgecolors='white', linewidth=0.6)
        ax.annotate(row['Province'], (row['Literacy'], row['Poverty']),
                    fontsize=6, color=TEXT_CLR, ha='center', va='bottom')
    ax.set_xlabel("Avg Literacy Rate (%)"); ax.set_ylabel("Avg Poverty Rate (%)")
    ax.set_title("Literacy vs Poverty (Bubble = Population)", color=TEXT_CLR, fontsize=10)
    _style(fig, [ax])
    return fig


# BONUS ── Pair Plot: Key socioeconomic indicators ────────────────────────────
def chart_pairplot(df: pd.DataFrame) -> plt.Figure:
    cols = ['Literacy_Rate','GDP_Per_Capita','Poverty_Rate','Life_Expectancy']
    sample = df[cols + ['Province']].sample(min(300, len(df)), random_state=42)
    provinces = sample['Province'].unique()
    palette = {p: PALETTE[i % len(PALETTE)] for i, p in enumerate(provinces)}
    g = sns.pairplot(sample, vars=cols, hue='Province',
                     palette=palette, diag_kind='kde',
                     plot_kws=dict(alpha=0.5, s=15),
                     diag_kws=dict(linewidth=1.2))
    g.fig.patch.set_facecolor(BG_CARD)
    for ax in g.axes.flatten():
        if ax:
            ax.set_facecolor(BG_CARD)
            ax.tick_params(colors=TEXT_CLR, labelsize=6)
            ax.xaxis.label.set_color(TEXT_CLR)
            ax.yaxis.label.set_color(TEXT_CLR)
            for spine in ax.spines.values():
                spine.set_edgecolor(GRID_CLR)
    g.fig.suptitle("Pair Plot — Key Socioeconomic Indicators",
                   color=TEXT_CLR, fontsize=10, y=1.01)
    return g.fig


# BONUS ── Funnel Chart: Urban-Rural breakdown ────────────────────────────────
def chart_funnel_urban_rural(df: pd.DataFrame) -> plt.Figure:
    data = df.groupby('Urban_Rural')['Population'].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    max_val = data.max()
    for i, (label, val) in enumerate(data.items()):
        width = (val / max_val) * 0.8
        left  = (1 - width) / 2
        ax.barh(i, width, left=left, color=PALETTE[i], height=0.55,
                edgecolor=BG_DARK, linewidth=0.5)
        ax.text(0.5, i, f'{label}  ({val/1e6:.1f}M)', ha='center', va='center',
                fontsize=8, color='white', fontweight='bold')
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("Population by Settlement Type (Funnel)", color=TEXT_CLR, fontsize=10)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.patch.set_facecolor(BG_CARD)
    ax.set_facecolor(BG_CARD)
    return fig