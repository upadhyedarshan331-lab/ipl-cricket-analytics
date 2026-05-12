# 05_eda_analysis.py
# PURPOSE: Exploratory Data Analysis - create charts from IPL data
# WHY: Visuals reveal patterns that numbers alone cannot show

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# ── SETUP ─────────────────────────────────────────────────────────────────────
plt.style.use('seaborn-v0_8-darkgrid')
OUTPUT_DIR = r"D:\I\ipl_p\reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── LOAD CLEAN DATA ───────────────────────────────────────────────────────────
print("Loading data...")
deliveries = pd.read_csv(r"D:\I\ipl_p\data\clean\deliveries_clean.csv")
matches    = pd.read_csv(r"D:\I\ipl_p\data\clean\matches_clean.csv")

# Merge deliveries with season info from matches
data = deliveries.merge(
    matches[['match_id', 'season', 'winner', 'venue', 'city']],
    on='match_id', how='left'
)

print(f"Total deliveries : {len(data):,}")
print(f"Total matches    : {data['match_id'].nunique():,}")
print(f"Seasons covered  : {data['season'].min()} to {data['season'].max()}")
print(f"Unique batters   : {data['batter'].nunique()}")
print(f"Unique bowlers   : {data['bowler'].nunique()}")

# ══════════════════════════════════════════════════════
# ANALYSIS 1: BATTING STATS
# ══════════════════════════════════════════════════════
print("\nCalculating batting stats...")

batting = data.groupby('batter').agg(
    matches    = ('match_id',     'nunique'),
    runs       = ('batsman_runs', 'sum'),
    balls      = ('batsman_runs', 'count'),
    fours      = ('is_four',      'sum'),
    sixes      = ('is_six',       'sum'),
    dismissals = ('is_wicket',    'sum')
).reset_index()

batting['strike_rate'] = (batting['runs'] / batting['balls'] * 100).round(2)
batting['average']     = (batting['runs'] / batting['dismissals'].replace(0, np.nan)).round(2)
batting['boundary_pct']= ((batting['fours'] + batting['sixes']) / batting['balls'] * 100).round(2)

# Minimum 500 balls for reliable stats
batting_q = batting[batting['balls'] >= 500].copy()
print(f"Qualified batters (500+ balls): {len(batting_q)}")

# ══════════════════════════════════════════════════════
# ANALYSIS 2: BOWLING STATS
# ══════════════════════════════════════════════════════
print("Calculating bowling stats...")

bowling = data.groupby('bowler').agg(
    matches = ('match_id',   'nunique'),
    balls   = ('total_runs', 'count'),
    runs    = ('total_runs', 'sum'),
    wickets = ('is_wicket',  'sum')
).reset_index()

bowling['overs']       = (bowling['balls'] / 6).round(1)
bowling['economy']     = (bowling['runs'] / (bowling['balls'] / 6)).round(2)
bowling['bowling_avg'] = (bowling['runs'] / bowling['wickets'].replace(0, np.nan)).round(2)
bowling['bowling_sr']  = (bowling['balls'] / bowling['wickets'].replace(0, np.nan)).round(1)

# Minimum 300 balls for reliable stats
bowling_q = bowling[bowling['balls'] >= 300].copy()
print(f"Qualified bowlers (300+ balls): {len(bowling_q)}")

# ══════════════════════════════════════════════════════
# ANALYSIS 3: PHASE-WISE STATS
# ══════════════════════════════════════════════════════
print("Calculating phase stats...")

phase = data.groupby('phase').agg(
    total_runs    = ('total_runs',    'sum'),
    total_balls   = ('batsman_runs',  'count'),
    total_wickets = ('is_wicket',     'sum'),
    sixes         = ('is_six',        'sum'),
    fours         = ('is_four',       'sum')
).reset_index()

phase['run_rate']         = (phase['total_runs'] / (phase['total_balls'] / 6)).round(2)
phase['wickets_per_over'] = (phase['total_wickets'] / (phase['total_balls'] / 6)).round(3)
phase_order = ['Powerplay', 'Middle', 'Death']
phase = phase.set_index('phase').loc[phase_order].reset_index()

# ══════════════════════════════════════════════════════
# ANALYSIS 4: SEASON TRENDS
# ══════════════════════════════════════════════════════
print("Calculating season trends...")

season = data.groupby('season').agg(
    matches    = ('match_id',    'nunique'),
    total_runs = ('total_runs',  'sum'),
    total_balls= ('batsman_runs','count'),
    sixes      = ('is_six',      'sum'),
    fours      = ('is_four',     'sum')
).reset_index()

season['run_rate'] = (season['total_runs'] / (season['total_balls'] / 6)).round(2)

# ══════════════════════════════════════════════════════
# CHART 1: TOP 10 RUN SCORERS
# ══════════════════════════════════════════════════════
print("\nGenerating charts...")

fig, ax = plt.subplots(figsize=(10, 6))
top10 = batting_q.nlargest(10, 'runs')
bars = ax.barh(top10['batter'], top10['runs'], color='steelblue', edgecolor='white')
ax.set_title('Top 10 IPL Run Scorers (All Time)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Total Runs', fontsize=12)
ax.invert_yaxis()
for bar, val in zip(bars, top10['runs']):
    ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
            f'{val:,}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'chart1_top_run_scorers.png'), dpi=150)
plt.close()
print("  ✓ Chart 1 saved: Top 10 Run Scorers")

# ══════════════════════════════════════════════════════
# CHART 2: STRIKE RATE VS AVERAGE (SCATTER)
# WHY: Shows player TYPE - aggressive vs consistent
# ══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(
    batting_q['average'],
    batting_q['strike_rate'],
    alpha=0.6, s=80,
    c=batting_q['runs'],
    cmap='YlOrRd'
)
plt.colorbar(scatter, label='Total Runs')

# Add reference lines
ax.axhline(y=batting_q['strike_rate'].mean(), color='gray',
           linestyle='--', alpha=0.5, label='Avg Strike Rate')
ax.axvline(x=batting_q['average'].mean(), color='gray',
           linestyle=':', alpha=0.5, label='Avg Average')

# Label top 8 run scorers
for _, row in batting_q.nlargest(8, 'runs').iterrows():
    ax.annotate(row['batter'].split()[-1],
                (row['average'], row['strike_rate']),
                fontsize=8, alpha=0.9,
                xytext=(5, 5), textcoords='offset points')

ax.set_title('Batting Average vs Strike Rate\n(Bubble size = Total Runs)',
             fontsize=13, fontweight='bold')
ax.set_xlabel('Batting Average', fontsize=12)
ax.set_ylabel('Strike Rate', fontsize=12)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'chart2_avg_vs_sr.png'), dpi=150)
plt.close()
print("  ✓ Chart 2 saved: Average vs Strike Rate")

# ══════════════════════════════════════════════════════
# CHART 3: PHASE-WISE RUN RATE
# ══════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

colors = ['#2ecc71', '#f39c12', '#e74c3c']

# Run Rate by phase
bars = axes[0].bar(phase['phase'], phase['run_rate'],
                   color=colors, edgecolor='white', width=0.5)
axes[0].set_title('Run Rate by Phase', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Runs per Over')
for bar, val in zip(bars, phase['run_rate']):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 str(val), ha='center', fontweight='bold', fontsize=11)

# Wickets per over by phase
bars2 = axes[1].bar(phase['phase'], phase['wickets_per_over'],
                    color=colors, edgecolor='white', width=0.5)
axes[1].set_title('Wickets per Over by Phase', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Wickets per Over')
for bar, val in zip(bars2, phase['wickets_per_over']):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                 str(val), ha='center', fontweight='bold', fontsize=11)

plt.suptitle('Phase-wise Match Analysis', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'chart3_phase_analysis.png'),
            dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Chart 3 saved: Phase Analysis")

# ══════════════════════════════════════════════════════
# CHART 4: TOP 10 WICKET TAKERS
# ══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 6))
top_bowl = bowling_q.nlargest(10, 'wickets')
bars = ax.barh(top_bowl['bowler'], top_bowl['wickets'],
               color='purple', edgecolor='white')
ax.set_title('Top 10 IPL Wicket Takers (All Time)',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Total Wickets', fontsize=12)
ax.invert_yaxis()
for bar, val in zip(bars, top_bowl['wickets']):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            str(int(val)), va='center', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'chart4_top_wicket_takers.png'), dpi=150)
plt.close()
print("  ✓ Chart 4 saved: Top Wicket Takers")

# ══════════════════════════════════════════════════════
# CHART 5: SEASON-WISE RUN RATE TREND
# ══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(season['season'], season['run_rate'],
        marker='o', color='steelblue', linewidth=2.5,
        markersize=8, markerfacecolor='white', markeredgewidth=2)
ax.fill_between(season['season'], season['run_rate'],
                alpha=0.1, color='steelblue')
for _, row in season.iterrows():
    ax.annotate(str(row['run_rate']),
                (row['season'], row['run_rate']),
                textcoords='offset points', xytext=(0, 10),
                ha='center', fontsize=8)
ax.set_title('IPL Run Rate Trend by Season',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Season', fontsize=12)
ax.set_ylabel('Runs per Over', fontsize=12)
ax.set_xticks(season['season'])
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'chart5_season_run_rate.png'), dpi=150)
plt.close()
print("  ✓ Chart 5 saved: Season Run Rate Trend")

# ══════════════════════════════════════════════════════
# CHART 6: SIXES PER SEASON
# ══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(season['season'], season['sixes'],
              color='gold', edgecolor='darkorange', linewidth=0.8)
ax.set_title('Total Sixes Hit per IPL Season',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Season', fontsize=12)
ax.set_ylabel('Number of Sixes', fontsize=12)
ax.set_xticks(season['season'])
ax.tick_params(axis='x', rotation=45)
for bar, val in zip(bars, season['sixes']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            str(int(val)), ha='center', fontsize=8, rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'chart6_sixes_per_season.png'), dpi=150)
plt.close()
print("  ✓ Chart 6 saved: Sixes per Season")

# ══════════════════════════════════════════════════════
# CHART 7: DISMISSAL TYPE BREAKDOWN
# ══════════════════════════════════════════════════════

dismissals = data[data['dismissal_kind'] != 'not_out']['dismissal_kind'].value_counts()

fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    dismissals.values,
    labels=dismissals.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=sns.color_palette('husl', len(dismissals))
)
ax.set_title('How Batters Get Out in IPL\n(Dismissal Type Breakdown)',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'chart7_dismissal_types.png'), dpi=150)
plt.close()
print("  ✓ Chart 7 saved: Dismissal Types")

# ══════════════════════════════════════════════════════
# EXPORT TABLES FOR POWER BI
# ══════════════════════════════════════════════════════
print("\nExporting analysis tables for Power BI...")

batting_q.to_csv(r"D:\I\ipl_p\data\analysis\batting_stats.csv",  index=False)
bowling_q.to_csv(r"D:\I\ipl_p\data\analysis\bowling_stats.csv",  index=False)
phase.to_csv    (r"D:\I\ipl_p\data\analysis\phase_stats.csv",    index=False)
season.to_csv   (r"D:\I\ipl_p\data\analysis\season_stats.csv",   index=False)

print("  ✓ batting_stats.csv exported")
print("  ✓ bowling_stats.csv exported")
print("  ✓ phase_stats.csv exported")
print("  ✓ season_stats.csv exported")

print("\n" + "="*55)
print("✅ EDA COMPLETE")
print("="*55)
print(f"7 charts saved to:       D:\\I\\ipl_p\\reports\\")
print(f"4 CSV files saved to:    D:\\I\\ipl_p\\data\\analysis\\")