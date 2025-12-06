#!/usr/bin/env python3
"""Quick test to verify data files load correctly"""
import pandas as pd
import os

print("Current directory:", os.getcwd())
print("\nFiles in current directory:")
for item in os.listdir('.'):
    print(f"  - {item}")

print("\nTrying to load data/weather.csv...")
try:
    df = pd.read_csv('data/weather.csv', nrows=5)
    print(f"✅ SUCCESS! Loaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\nTrying to load data/metro.csv...")
try:
    df = pd.read_csv('data/metro.csv')
    print(f"✅ SUCCESS! Loaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
except Exception as e:
    print(f"❌ FAILED: {e}")
