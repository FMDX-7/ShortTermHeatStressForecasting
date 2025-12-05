import pandas as pd
import numpy as np

weather = pd.read_csv('weather.csv')
metro = pd.read_csv('metro.csv')

print("=== WEATHER DATA ===")
print("Columns:", weather.columns.tolist())
print("Shape:", weather.shape)
print("\nFirst row:")
print(weather.iloc[0])

print("\n=== METRO DATA ===")
print("Columns:", metro.columns.tolist())
print("Shape:", metro.shape)
print("\nAll metro data:")
print(metro)

print("\n=== DATA MATCHING CHECK ===")
if 'county' in weather.columns:
    print("Weather 'county' values:", weather['county'].unique()[:5])
else:
    print("No 'county' column in weather")
    
print("Metro 'county' values:", metro['county'].unique()[:10])
