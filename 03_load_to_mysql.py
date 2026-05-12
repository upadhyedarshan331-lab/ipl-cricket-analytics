# 03_load_to_mysql.py
# PURPOSE: Load clean CSV data into MySQL database
# WHY: So we can query data using SQL instead of loading CSVs every time

import pandas as pd
import mysql.connector
from mysql.connector import Error

# ── CONNECT TO MYSQL ──────────────────────────────────────────────────────────
# WHY: Python needs credentials to talk to your MySQL database
# Change 'your_password' to your actual MySQL root password

try:
    conn = mysql.connector.connect(
        host     = 'localhost',
        user     = 'root',
        password = 'koenigsegg0',   # ← CHANGE THIS to your MySQL password
        database = 'ipl_analytics'
    )
    cursor = conn.cursor()
    print("✅ Connected to MySQL successfully")
except Error as e:
    print(f"❌ Connection failed: {e}")
    print("Check: Is MySQL running? Is your password correct?")
    exit()

# ── LOAD CLEAN DATA ───────────────────────────────────────────────────────────
print("\nLoading clean CSV files...")
deliveries = pd.read_csv(r"D:\I\ipl_p\data\clean\deliveries_clean.csv")
matches    = pd.read_csv(r"D:\I\ipl_p\data\clean\matches_clean.csv")
print(f"Deliveries: {len(deliveries):,} rows")
print(f"Matches:    {len(matches):,} rows")

# ── STEP 1: INSERT VENUES ─────────────────────────────────────────────────────
# WHY: Venues must exist before matches (foreign key rule)
print("\n[1/4] Inserting venues...")
venues = matches['venue'].dropna().unique()
for venue in venues:
    cursor.execute(
        "INSERT IGNORE INTO venues (venue_name) VALUES (%s)",
        (str(venue),)
    )
conn.commit()

# Build venue lookup dictionary: name → id
cursor.execute("SELECT venue_id, venue_name FROM venues")
venue_map = {name: vid for vid, name in cursor.fetchall()}
print(f"      {len(venue_map)} venues inserted")

# ── STEP 2: INSERT MATCHES ────────────────────────────────────────────────────
# WHY: Matches must exist before deliveries (foreign key rule)
print("\n[2/4] Inserting matches...")
inserted = 0
skipped  = 0

for _, r in matches.iterrows():
    venue_id = venue_map.get(str(r.get('venue', '')), None)
    try:
        cursor.execute("""
            INSERT IGNORE INTO matches
            (match_id, season, match_date, city, venue_id,
             team1, team2, toss_winner, toss_decision,
             winner, result, result_margin, player_of_match, method)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            int(r['match_id']),
            int(r['year'])            if pd.notna(r.get('year'))           else None,
            str(r['date'])[:10]       if pd.notna(r.get('date'))           else None,
            r.get('city',       'Unknown'),
            venue_id,
            r.get('team1',      'Unknown'),
            r.get('team2',      'Unknown'),
            r.get('toss_winner','Unknown'),
            r.get('toss_decision', 'bat'),
            r.get('winner',     'No Result'),
            r.get('result',     'Normal'),
            float(r['result_margin']) if pd.notna(r.get('result_margin'))  else None,
            r.get('player_of_match', 'Unknown'),
            r.get('method',     'Normal')
        ))
        inserted += 1
    except Exception as e:
        skipped += 1
conn.commit()
print(f"      {inserted} matches inserted, {skipped} skipped")

# ── STEP 3: INSERT PLAYERS ────────────────────────────────────────────────────
# WHY: Players table must be filled before deliveries references batter/bowler
print("\n[3/4] Inserting players...")
all_players = set(
    deliveries['batter'].dropna().tolist() +
    deliveries['bowler'].dropna().tolist() +
    deliveries['player_dismissed'].dropna().tolist()
)
all_players.discard('none')   # Remove the 'none' placeholder we added

for player in all_players:
    cursor.execute(
        "INSERT IGNORE INTO players (player_name) VALUES (%s)",
        (str(player),)
    )
conn.commit()

# Build player lookup dictionary: name → id
cursor.execute("SELECT player_id, player_name FROM players")
player_map = {name: pid for pid, name in cursor.fetchall()}
print(f"      {len(player_map)} players inserted")

# ── STEP 4: INSERT DELIVERIES ─────────────────────────────────────────────────
# WHY: Largest table - we insert in batches of 1000 for speed
print("\n[4/4] Inserting deliveries (this takes 2-3 minutes)...")

batch      = []
batch_size = 1000
inserted   = 0
skipped    = 0

for _, r in deliveries.iterrows():
    batter_id    = player_map.get(str(r['batter']))
    bowler_id    = player_map.get(str(r['bowler']))
    dismissed_id = player_map.get(str(r.get('player_dismissed', 'none')))

    # Skip row if batter or bowler not found in players table
    if not batter_id or not bowler_id:
        skipped += 1
        continue

    batch.append((
        int(r['match_id']),
        int(r['inning']),
        r.get('batting_team', ''),
        r.get('bowling_team', ''),
        int(r['over']),
        int(r['ball']),
        batter_id,
        bowler_id,
        int(r.get('batsman_runs', 0)),
        int(r.get('extra_runs',   0)),
        int(r.get('total_runs',   0)),
        r.get('extras_type', 'normal'),
        int(r.get('is_wicket',   0)),
        r.get('dismissal_kind', 'not_out'),
        dismissed_id,
        r.get('phase', 'Middle'),
        int(r.get('is_four',     0)),
        int(r.get('is_six',      0)),
        int(r.get('is_boundary', 0))
    ))

    # Insert in batches
    if len(batch) >= batch_size:
        cursor.executemany("""
            INSERT INTO deliveries
            (match_id, inning, batting_team, bowling_team,
             over_num, ball_num, batter_id, bowler_id,
             batsman_runs, extra_runs, total_runs, extras_type,
             is_wicket, dismissal_kind, player_dismissed_id,
             phase, is_four, is_six, is_boundary)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, batch)
        conn.commit()
        inserted += len(batch)
        print(f"      {inserted:,} rows inserted so far...")
        batch = []

# Insert remaining rows
if batch:
    cursor.executemany("""
        INSERT INTO deliveries
        (match_id, inning, batting_team, bowling_team,
         over_num, ball_num, batter_id, bowler_id,
         batsman_runs, extra_runs, total_runs, extras_type,
         is_wicket, dismissal_kind, player_dismissed_id,
         phase, is_four, is_six, is_boundary)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, batch)
    conn.commit()
    inserted += len(batch)

print(f"\n      Total inserted: {inserted:,}")
print(f"      Total skipped:  {skipped:,}")

# ── FINAL VERIFICATION ────────────────────────────────────────────────────────
print("\n--- Verification ---")
for table in ['venues', 'matches', 'players', 'deliveries']:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table:12} → {count:,} rows")

cursor.close()
conn.close()

print("\n" + "="*55)
print("✅ ALL DATA LOADED INTO MYSQL SUCCESSFULLY")
print("="*55)