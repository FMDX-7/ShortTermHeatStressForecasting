# 🌤️ NYC Metro HSRI Weather Dashboard

**Heat Stress Risk Index** • Real-time conditions & clothing recommendations

A real-time monitoring and forecasting system designed to reduce heat-related health impacts across the NYC metropolitan region through predictive analytics and geographic risk assessment.

---

## 📊 Project Overview

This Heat Stress Risk Index (HSRI) Weather Dashboard is a real-time monitoring and forecasting system designed to reduce heat-related health impacts across the NYC metropolitan region. Developed as part of Cornell University's SYSEN 5300 course, this project demonstrates predictive analytics for public health resilience.

### Project Goals
- **Reduce hospital admissions** by 20% through early warning and targeted interventions
- **Lower healthcare costs** by 40% via proactive cooling center placement and resource allocation
- **Improve equity** by providing neighborhood-level forecasts for vulnerable populations
- **Enable data-driven decision-making** for city planners, public health officials, and emergency managers

---
## 👤 Team
- **Members**: Fabien M. De Silva Jr. <fmd48@cornell.edu> | Jose Ruben Salinas Aguilar <js3873@cornell.edu> | Anggasta Anindityo <aa2938@cornell.edu>
- **Institution**: Cornell University, SYSEN
- **Course**: SYSEN 5300 - Systems Engineering and Six Sigma
- **Year**: Fall 2025
---

## 🚀 Quick Start

### Access the Dashboard
The dashboard is deployed and accessible online. Navigate to the main interface to:
1. Select a date and time from the sidebar
2. Choose an NYC borough/area or view "All Areas"
3. Adjust the HSRI Risk Threshold to filter high-risk locations
4. View real-time metrics, forecasts, and interactive maps

### Run Locally

```bash
# Clone the repository
git clone https://github.com/FMDX-7/ShortTermHeatStressForecasting.git
cd ShortTermHeatStressForecasting

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📈 How It Works

### Heat Stress Risk Index (HSRI)
The HSRI combines multiple meteorological variables into a single indicator of heat stress risk:

**Formula:**
```
HSRI = HI + 0.3·UV + 8·SR_eff − 4·WS − 0.05·CC
```

Where:
- **HI**: NWS Heat Index (temperature + humidity effect)
- **UV**: UV Index (radiant heat load, 0-10+)
- **SR_eff**: Effective solar radiation (normalized, ~0-1)
- **WS**: Wind speed (mph, cooling effect)
- **CC**: Cloud cover (%, shading effect)

### Risk Categories
- 🔴 **Critical** (HSRI ≥85): Extreme danger - activate all emergency protocols
- 🟠 **High** (HSRI 75-84): Significant risk - increase cooling center capacity
- 🟡 **Moderate** (HSRI 65-74): Moderate risk - monitor vulnerable populations
- 🟢 **Low** (HSRI 50-64): Mild conditions - routine operations
- 🔵 **Cool** (HSRI 30-49): Cool conditions - normal operations
- 🟣 **Freezing** (HSRI <30): Winter conditions - winter coat recommended

---

## 🗺️ Dashboard Features

### 📊 Dashboard Tab
- Real-time HSRI metrics (average, peak, distribution across sites)
- Borough/area filtering for localized analysis
- 3-day HSRI forecast with trend visualization
- Operational insights (cooling center readiness, affected counties, healthcare alerts)
- Interactive Folium map with color-coded risk markers
- Expandable risk level legend with detailed protective clothing guidance

### 🌦️ Weather Details Tab
- Expandable detailed weather conditions for each monitoring site
- All 6 meteorological variables with units
- HSRI output and risk categorization for each location
- High-risk location data table with sorting and filtering
- Displays "N/A" for unavailable data (solar, UV, cloud cover for historical periods)

### ℹ️ About Tab
- Comprehensive project background and goals
- Technical documentation and architecture
- Model performance metrics (R² = 0.965)
- Data sources and geographic coverage
- Interpretation guides for different user roles
- Clothing recommendations for each risk level

---

## 📍 Geographic Coverage

**56 AQS Monitoring Stations** across 12 regions:

- **NYC (5 Boroughs)**: Manhattan (3), Brooklyn, Queens (2), Bronx (2), Staten Island (2)
- **Westchester County**: 3 stations
- **Long Island**: Nassau (8), Suffolk (4)
- **Surrounding Areas**: New Jersey (1), Connecticut (3)
- **Northern NY**: Rockland (2), Orange/Dutchess/Putnam (3)

---

## 💾 Data & Model

### Data Source
- **Weather Data**: Hourly observations from 56 AQS (Air Quality System) monitoring stations
- **Geographic Coverage**: NYC metro region with complete borough and county coverage
- **Time Period**: 2018-01-01 to 2025-06-01 (continuous hourly records)
- **Variables**: Temperature, humidity, wind speed, solar radiation, UV index, cloud cover
- **Records**: 1,177,767 hourly observations
- **Data Quality**: Core meteorological parameters (temp, humidity, wind) required; solar/UV/cloud optional

### Forecasting Model
- **Algorithm**: Linear Regression
- **Model Accuracy**: R² = 0.965, RMSE = 3.0°F, MAE = 2.19°F
- **Horizon**: 1-3 day advance forecasts
- **Rationale**: Prioritizes interpretability and operational feasibility
- **Training Data**: Historical HSRI with all 6 meteorological features

---

## 🎯 Sidebar Controls

### Time Selection
- **Date Picker**: Choose observation date (defaults to earliest available)
- **Hour Selector**: Select specific hour 0-23 UTC (defaults to 0)

### Filtering
- **HSRI Risk Threshold**: Number input, range -100 to 100, default 65

### Geographic Selection
- **Borough/Area Dropdown**: 12 predefined regions with available data only

---

## 👕 Clothing Recommendations

- 🔴 **Critical (85+)**: Loose-fitting light-colored breathable fabrics, wide-brimmed hat, sunglasses
- 🟠 **High (75-84)**: Shorts + T-Shirt, light colors, stay hydrated
- 🟡 **Moderate (65-74)**: Short sleeves, light layers
- 🟢 **Low (50-64)**: Light layers, normal outdoor activities
- 🔵 **Cool (30-49)**: Light jacket, long sleeves
- 🟣 **Freezing (<30)**: Winter coat, warm layers, gloves, hat, scarf

---

## 👥 User Guides

### For Public Health Officials
- Monitor **Peak HSRI** to trigger emergency protocols
- Use **High-Risk Sites** for resource allocation
- Review **Most Affected County** for targeted interventions

### For City Planners
- Use **3-Day Forecast** for advance planning
- Identify vulnerable areas through **HSRI Distribution**
- Plan tree canopy and green space improvements

### For Residents
- Follow **Protective Clothing Guide**
- Monitor **Peak HSRI** for activity planning
- Check **Forecast** for future conditions

---

## 🛠️ Technical Stack

- **Framework**: Streamlit 1.40.1
- **Data Processing**: Pandas 2.2.0, NumPy 1.24.3
- **Visualization**: Plotly 5.18.0, Folium 0.14.0, Streamlit-Folium 0.19.0
- **ML**: scikit-learn LinearRegression
- **Deployment**: Cloud-ready for Streamlit Community Cloud

---

## 📦 Requirements

```bash
pip install -r requirements.txt
```

---

## 📚 Documentation

Full documentation in `docs/` folder:
- **DASHBOARD_USER_GUIDE.md** - User guide
- **TECHNICAL_ARCHITECTURE.md** - Technical details
- **QUICK_START.md** - Setup guide

---

## 🔗 Resources

- [NWS Heat Index](https://www.weather.gov/media/epz/wxcalc/heatIndex.pdf)
- [EPA UV Index Guide](https://www.epa.gov/sites/production/files/2015-09/documents/UV_Index_10.pdf)
- [CDC Heat Stress Prevention](https://www.cdc.gov/niosh/topics/emres/cheathstress.html)
- [NYC OEM](https://www1.nyc.gov/site/em/index.page)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Attribution Required
If you use this code or dashboard, please credit:
- **Fabien M. De Silva Jr.** (fmd48@cornell.edu)
- **Jose Ruben Salinas Aguilar** (js3873@cornell.edu)
- **Anggasta Anindityo** (aa2938@cornell.edu)
- **Cornell University, SYSEN 5300**

### Data Sources
- **Weather data**: EPA AQS (public domain)
- **Geographic data**: U.S. Census Bureau (public domain)

---

**Last Updated: December 2025**

*Reducing heat-related health impacts through predictive analytics.*
