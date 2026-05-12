# 🏏 IPL Cricket Analytics Project

End to end cricket analytics project analyzing 17 seasons 
of IPL using Python, MySQL, Power BI and Excel.

---

## 🛠️ Tools Used
- Python (pandas, matplotlib, seaborn)
- MySQL
- Power BI
- Excel

---

## 📊 Dataset
- Source: Kaggle IPL Complete Dataset
- 260,920 deliveries across 1,095 matches
- Seasons 2008 to 2024
- 732 unique players across 58 venues

---

## 🗂️ Project Structure

ipl-cricket-analytics/
├── scripts/
│   ├── 00_check_columns.py
│   ├── 01_data_cleaning.py
│   ├── 03_load_to_mysql.py
│   └── 05_eda_analysis.py
├── sql/
│   ├── 02_database_setup.sql
│   └── 04_analysis_queries.sql
├── reports/
│   └── (7 EDA charts)
└── README.md

---

## ⚙️ How to Run
1. Download IPL dataset from Kaggle
2. Run `scripts/01_data_cleaning.py`
3. Run `sql/02_database_setup.sql` in MySQL Workbench
4. Run `scripts/03_load_to_mysql.py`
5. Run `scripts/05_eda_analysis.py`
6. Open Power BI dashboard

---

## 🔍 Key Insights
1. 64% of captains choose to field after winning toss
2. 62% of all dismissals are caught
3. Death overs have highest run rate of all phases
4. Six hitting has increased every IPL season

---

## 📈 Dashboard Pages

### Page 1 — Overview
- 4 KPI cards (matches, runs, sixes, wickets)
- Run rate trend by season
- Matches played per season

### Page 2 — Batting Analysis
- Top 10 run scorers bar chart
- Average vs Strike Rate scatter chart
- Full batting scorecard table

### Page 3 — Match Insights
- Run rate by phase
- Toss decision distribution
- Sixes per season
- Dismissal type breakdown

---

## 📸 Charts

### Top 10 Run Scorers
![Top Run Scorers](reports/chart1_top_run_scorers.png)

### Average vs Strike Rate
![Avg vs SR](reports/chart2_avg_vs_sr.png)

### Phase Analysis
![Phase](reports/chart3_phase_analysis.png)

### Season Run Rate Trend
![Season](reports/chart5_season_run_rate.png)

### Dismissal Types
![Dismissals](reports/chart7_dismissal_types.png)

---

## 🗄️ Database Schema

venues     (58 rows)   — all IPL stadiums
matches    (1,095 rows) — every match played
players    (732 rows)  — every unique player
deliveries (260,920 rows) — every ball bowled

---

## 📋 SQL Queries
1. Top 10 run scorers
2. Top 10 wicket takers
3. Phase-wise run rate
4. Toss impact analysis
5. Death over specialists
6. Best powerplay bowlers
7. Season-wise trends
8. Venue-wise scores
9. Batting partnerships
10. Dismissal breakdown
