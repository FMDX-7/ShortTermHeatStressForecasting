# NYC HSRI Dashboard - Quick Start Guide

## Overview
This dashboard provides real-time Heat Stress Risk Index (HSRI) monitoring across NYC Metro (22 counties) with predictive capabilities for public health decision-making.

## Dashboard Components

### 1. **Key Metrics Bar** (Top of Page)
Shows at-a-glance heat stress summary:
- **📊 Avg HSRI:** Average heat stress across all sites
- **🔥 Peak HSRI:** Maximum heat stress detected with risk category
- **⚠️ High-Risk Sites:** Number of locations exceeding threshold
- **🌡️ Avg Temp:** Average temperature across region
- **💧 Avg Humidity:** Average humidity levels

### 2. **Geographic Heat Risk Map** (Center Left)
- **Interactive Folium Map** showing all monitoring stations
- **Color-Coded Markers:**
  - 🔴 Red = Critical (HSRI ≥ 85)
  - 🟠 Orange = High (HSRI ≥ 75)
  - 🟡 Yellow = Moderate (HSRI ≥ 65)
  - 🟢 Green = Low (HSRI ≥ 50)
  - 🔵 Blue = Cool (HSRI < 50)
- **Click markers** for detailed site information
- **Hover** to see site name and HSRI value

### 3. **Risk Legend** (Right Sidebar)
Quick reference for heat stress categories and HSRI ranges.

### 4. **High-Risk Location Details** (Data Table)
Detailed metrics for locations exceeding your selected threshold:
- Site Name & County
- Current Temperature (°F)
- Humidity (%)
- Wind Speed (mph)
- Solar Radiation (W/m²)
- UV Index
- Cloud Cover (%)
- HSRI Value
- Risk Level

### 5. **HSRI Distribution Chart** (Bottom Left)
- Histogram showing spread of heat stress across all sites
- Red dashed line shows your selected threshold
- Interactive Plotly chart—hover for exact values

### 6. **3-Day HSRI Forecast** (Bottom Right)
- Line graph with predicted HSRI for next 3 days
- Based on Linear Regression model (R² = 0.965)
- Threshold line for easy comparison
- Toggle in sidebar to enable/disable

### 7. **Operational Insights** (Lower Section)
Three key metrics for decision-makers:
- **🏢 Cooling Centers to Activate:** How many of your facilities should be operational
- **📍 Most Affected County:** Primary focus area for interventions
- **🏥 Healthcare Alert Level:** Expected strain on emergency services

### 8. **Protective Clothing Guide** (Lower Section)
Visual guide showing recommended clothing by HSRI level and associated risk.

### 9. **Formula & Metadata** (Footer)
- HSRI calculation formula
- Model accuracy (R² = 0.965, RMSE = 3.0°F)
- Update frequency and forecast horizon
- Last update timestamp

---

## Sidebar Controls

### ⚙️ Dashboard Controls

**📅 Select Time**
- Slider to choose specific date and hour (hourly granularity)
- Loads nearest available data point
- Default: Most recent available data

**🌡️ HSRI Risk Threshold**
- Slider from 30–130
- Filters table and marker display
- Default: 65 (Moderate risk)
- Higher values show only most critical situations

**📈 Show 3-Day Forecast**
- Toggle to enable/disable forecast section
- Useful for operational planning
- Default: Enabled

### 📊 Project Info
Displays project overview, model accuracy, and coverage information.

---

## How to Use for Different Scenarios

### **Morning Planning (6 AM)**
1. Keep threshold at 65 to identify developing heat stress
2. Check forecast to anticipate afternoon peaks
3. Note most affected counties for early staff deployment
4. Review cooling center activation count

### **Heat Emergency Response**
1. Lower threshold to 75+ to focus on critical areas
2. Use map to dispatch resources to red/orange zones
3. Check healthcare alert level to notify hospitals
4. Monitor real-time changes by refreshing hourly

### **Public Health Communication**
1. Identify high-risk locations by county (table view)
2. Use clothing guide to communicate protective measures
3. Reference HSRI values (not just daily forecasts) for accuracy
4. Highlight most affected vulnerable populations

### **Research/Validation**
1. Adjust time slider to review historical patterns
2. Compare HSRI forecast vs. actual outcomes
3. Use data table for detailed meteorological patterns
4. Track correlation between HSRI and operational decisions

---

## Understanding HSRI Values

| HSRI Range | Category | Risk Level | Action |
|-----------|----------|-----------|--------|
| ≥ 85 | Critical Heat | 🔴 CRITICAL | Activate all cooling centers, hospital alert, emergency warnings |
| 75-84 | High Heat | 🟠 HIGH | Activate most facilities, public advisories, monitor vulnerable populations |
| 65-74 | Moderate Heat | 🟡 MODERATE | Standby resources, public awareness, check on elderly/disabled |
| 50-64 | Mild | 🟢 LOW | Normal operations, routine hydration reminders |
| < 50 | Cool | 🔵 COOL | Normal seasonal operations |

---

## Key Features for Different Users

### **Emergency Managers**
- Real-time geographic heat stress visualization
- County-level decision support
- Cooling center activation calculator (40% cost savings vs. reactive approach)
- Forecast for 1-3 day planning horizon

### **Healthcare Providers**
- Expected admission patterns by heat stress level
- 3-hour advance warning capability (newspaper to ED visit = ~3 hours)
- Vulnerable population targeting (HSRI-based equity metrics)
- Risk level alerts for surge capacity planning

### **City Planners**
- Neighborhood hotspot identification
- County comparison analytics
- Historical trend analysis (time slider)
- Integration point for cooling center network

### **Research Community**
- Detailed meteorological data (temp, humidity, wind, solar, UV, clouds)
- Model accuracy transparency (R², RMSE, MAE displayed)
- 1-3 day forecast validation capability
- County-level geographic granularity

---

## Technical Details

**Model:** Linear Regression (recommended for production)
- Training Data: 2018-2019 and 2024-2025 hourly observations
- R² Score: 0.965 (explains 96.5% of variance)
- RMSE: 3.0°F
- MAE: 2.19°F

**HSRI Formula:**
```
HSRI = HI_base + (0.3 × UV_index) + (8 × Solar_Radiation/1000) 
       - (4 × Wind_Speed) - (0.05 × Cloud_Cover)
```

**Geographic Coverage:**
- NYC: Manhattan, Queens, Brooklyn, Bronx, Staten Island
- Westchester: Westchester, Rockland, Putnam, Suffolk, Nassau
- New Jersey: Bergen, Hudson, Passaic, Middlesex, Monmouth, Ocean, Somerset, Essex, Union, Morris, Sussex, Hunterland

---

## Troubleshooting

**❌ No data available for selected time**
- CSV may be incomplete for that time period
- Try selecting a different hour
- Check data source for available date range

**❌ metro.csv not found warning**
- Place `metro.csv` in same directory as `app.py`
- Dashboard will still work with hardcoded county data

**❌ Forecast not showing**
- Requires ≥10 historical data points
- May need more complete weather dataset
- Check that all weather variables are present (temp, humidity, wind, solar, UV, clouds)

**⚠️ Unexpected HSRI values**
- HSRI is clipped to 30-130 range (human comfort scale)
- Verify weather CSV has valid numeric values
- Check for missing or null weather fields

---

## Contact & Support

**Project:** Short-Term Heat Stress Forecasting for Health Risk Mitigation  
**Course:** SYSEN 5300 - Cornell University  
**Team:** Anggasta Anindityo, Fabien De Silva Jr., Jose Ruben Salinas Aguilar  

For questions about model or data interpretation, refer to project documentation.

---

**Last Updated:** December 4, 2025  
**Dashboard Version:** 1.0  
**Status:** Production Ready ✅
