import pandas as pd
import os

deliveries_path = r"D:\I\ipl_p\data\raw\deliveries.csv"
matches_path    = r"D:\I\ipl_p\data\raw\matches.csv"

if not os.path.exists(deliveries_path):
    print("ERROR: deliveries.csv not found")
    print("Check that it is inside D:\\I\\ipl_p\\data\\raw\\")
    exit()

if not os.path.exists(matches_path):
    print("ERROR: matches.csv not found")
    print("Check that it is inside D:\\I\\ipl_p\\data\\raw\\")
    exit()

deliveries = pd.read_csv(deliveries_path)
matches    = pd.read_csv(matches_path)

print("="*55)
print("DELIVERIES.CSV")
print("="*55)
print(f"Rows: {len(deliveries):,}   Columns: {len(deliveries.columns)}")
print("\nColumn names:")
for i, col in enumerate(deliveries.columns, 1):
    print(f"  {i:2}. {col}")

print("\n" + "="*55)
print("MATCHES.CSV")
print("="*55)
print(f"Rows: {len(matches):,}   Columns: {len(matches.columns)}")
print("\nColumn names:")
for i, col in enumerate(matches.columns, 1):
    print(f"  {i:2}. {col}")

print("\nDone. Copy everything above and share it.")