# 01_data_cleaning.py
# PURPOSE: Clean your raw IPL data and save ready-to-use files
# Your exact columns are used here - no guessing

import pandas as pd
import numpy as np
import os

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
deliveries = pd.read_csv(r"D:\I\ipl_p\data\raw\deliveries.csv")
matches    = pd.read_csv(r"D:\I\ipl_p\data\raw\matches.csv")

print(f"Loaded deliveries: {len(deliveries):,} rows")
print(f"Loaded matches:    {len(matches):,} rows")

# ── STEP 1: RENAME COLUMNS FOR CONSISTENCY ────────────────────────────────────
# WHY: matches.csv uses 'id' but deliveries uses 'match_id'
# We rename 'id' to 'match_id' so both files speak the same language

matches.rename(columns={'id': 'match_id'}, inplace=True)
print("\n✓ Renamed 'id' to 'match_id' in matches")

# ── STEP 2: HANDLE MISSING VALUES ─────────────────────────────────────────────
# WHY: NaN in dismissal_kind means no wicket fell - that is valid data, not missing

# Deliveries
deliveries['dismissal_kind']   = deliveries['dismissal_kind'].fillna('not_out')
deliveries['player_dismissed'] = deliveries['player_dismissed'].fillna('none')
deliveries['fielder']          = deliveries['fielder'].fillna('none')
deliveries['extras_type']      = deliveries['extras_type'].fillna('normal')

# Matches
matches['winner']          = matches['winner'].fillna('No Result')
matches['player_of_match'] = matches['player_of_match'].fillna('Unknown')
matches['city']            = matches['city'].fillna('Unknown')
matches['method']          = matches['method'].fillna('Normal')

print("✓ Missing values handled")

# ── STEP 3: REMOVE DUPLICATES ──────────────────────────────────────────────────
before = len(deliveries)
deliveries.drop_duplicates(inplace=True)
print(f"✓ Duplicates removed from deliveries: {before - len(deliveries)}")

before = len(matches)
matches.drop_duplicates(inplace=True)
print(f"✓ Duplicates removed from matches: {before - len(matches)}")

# ── STEP 4: FIX DATA TYPES ────────────────────────────────────────────────────
# WHY: Ensures numbers are numbers, dates are dates

deliveries['over']         = deliveries['over'].astype(int)
deliveries['ball']         = deliveries['ball'].astype(int)
deliveries['is_wicket']    = deliveries['is_wicket'].astype(int)
deliveries['batsman_runs'] = deliveries['batsman_runs'].astype(int)
deliveries['extra_runs']   = deliveries['extra_runs'].astype(int)
deliveries['total_runs']   = deliveries['total_runs'].astype(int)

matches['date'] = pd.to_datetime(matches['date'], errors='coerce')
matches['year'] = matches['date'].dt.year

print("✓ Data types fixed")

# ── STEP 5: STRIP WHITESPACE FROM TEXT COLUMNS ────────────────────────────────
# WHY: "MS Dhoni " and "MS Dhoni" are treated as different players without this

for col in deliveries.select_dtypes(include='object').columns:
    deliveries[col] = deliveries[col].str.strip()

for col in matches.select_dtypes(include='object').columns:
    matches[col] = matches[col].str.strip()

print("✓ Whitespace stripped from all text columns")

# ── STEP 6: ADD PHASE COLUMN ───────────────────────────────────────────────────
# WHY: Phase (Powerplay/Middle/Death) is the most important cricket insight
# Overs 1-6 = Powerplay, 7-15 = Middle, 16-20 = Death

def assign_phase(over):
    if over <= 5:
        return 'Powerplay'
    elif over <= 14:
        return 'Middle'
    else:
        return 'Death'

deliveries['phase'] = deliveries['over'].apply(assign_phase)
print("✓ Phase column added (Powerplay / Middle / Death)")

# ── STEP 7: ADD BOUNDARY FLAGS ────────────────────────────────────────────────
# WHY: Makes analysis faster - no need to filter every time

deliveries['is_four']     = (deliveries['batsman_runs'] == 4).astype(int)
deliveries['is_six']      = (deliveries['batsman_runs'] == 6).astype(int)
deliveries['is_boundary'] = (deliveries['batsman_runs'].isin([4, 6])).astype(int)

print("✓ Boundary flags added (is_four, is_six, is_boundary)")

# ── STEP 8: VALIDATE DATA ─────────────────────────────────────────────────────
# WHY: Sanity check - make sure nothing broke during cleaning

print("\n--- Validation Checks ---")

assert (deliveries['batsman_runs'] >= 0).all(), "ERROR: Negative runs found!"
print("✓ No negative runs")

assert deliveries['over'].between(0, 19).all(), "ERROR: Invalid over numbers!"
print("✓ All over numbers valid (0 to 19)")

assert deliveries['is_wicket'].isin([0, 1]).all(), "ERROR: Bad is_wicket values!"
print("✓ is_wicket column valid (only 0 and 1)")

missing_matches = ~deliveries['match_id'].isin(matches['match_id'])
print(f"✓ Deliveries with no matching match: {missing_matches.sum()}")

print(f"\nPhase distribution:")
print(deliveries['phase'].value_counts())

print(f"\nTotal wickets in dataset: {deliveries['is_wicket'].sum():,}")
print(f"Total boundaries:         {deliveries['is_boundary'].sum():,}")
print(f"Total sixes:              {deliveries['is_six'].sum():,}")

# Fix season format — convert "2007/08" to 2008 (use ending year)
def clean_season(s):
    s = str(s).strip()
    if '/' in s:
        return int('20' + s.split('/')[1]) if len(s.split('/')[1]) == 2 else int(s.split('/')[1])
    else:
        return int(s)

matches['season'] = matches['season'].apply(clean_season)
print("✓ Season format cleaned")

# ── STEP 9: SAVE CLEAN DATA ───────────────────────────────────────────────────
# WHY: We never touch raw data again. All future scripts use clean data.

deliveries.to_csv(r"D:\I\ipl_p\data\clean\deliveries_clean.csv", index=False)
matches.to_csv(r"D:\I\ipl_p\data\clean\matches_clean.csv", index=False)

print("\n" + "="*55)
print("✅ CLEANING COMPLETE")
print("="*55)
print(f"deliveries_clean.csv → {len(deliveries):,} rows, {len(deliveries.columns)} columns")
print(f"matches_clean.csv    → {len(matches):,} rows, {len(matches.columns)} columns")
print("\nClean files saved to D:\\I\\ipl_p\\data\\clean\\")