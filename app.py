#!/usr/bin/env python3
"""
HSRI Weather Dashboard - Streamlit App
Interactive map showing HSRI, temperature, and clothing recommendations across NYC metro.
Uses metro.csv for county-level geographic information.
Deploy to Streamlit Cloud with: streamlit cloud deploy
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="NYC HSRI Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌤️ NYC Metro HSRI Weather Dashboard")
st.markdown("**Heat Stress Risk Index** • Real-time conditions & clothing recommendations")

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_weather_data(filepath='data/weather.csv'):
    """Load and preprocess weather CSV, filtering for core meteorological data."""
    df = pd.read_csv(filepath)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Filter for rows with core meteorological parameters only
    required_cols = ['temp', 'humidity', 'windspeed']
    df = df.dropna(subset=required_cols)
    
    # Keep solar radiation, UV index, and cloud cover as-is (with NaN for missing values)
    # These will be handled as "N/A" in display
    
    return df

@st.cache_data
def load_metro_data(filepath='data/metro.csv'):
    """Load metro area county data."""
    try:
        metro_df = pd.read_csv(filepath)
        return metro_df
    except FileNotFoundError:
        return None

def load_site_data(weather_df=None):
    """Load site metadata - dynamically from weather data or defaults."""
    if weather_df is None:
        weather_df = load_weather_data()
    
    # Get unique AQS IDs from weather data
    unique_aqs_ids = weather_df['aqs_id_full'].unique()
    
    # Create mapping for known/major NYC metro AQS IDs
    aqs_mapping = {
        # NYC (5 Boroughs)
        840421010055: ('Manhattan-Midtown', 'New York County', 40.7614, -73.9776),
        840421010075: ('Manhattan-Upper West', 'New York County', 40.7831, -73.9712),
        840421010048: ('Manhattan-Upper East', 'New York County', 40.7688, -73.9519),
        840090010010: ('Brooklyn-Downtown', 'Kings County', 40.6501, -73.9496),
        
        # Queens
        840360470052: ('Queens-Astoria', 'Queens County', 40.7673, -73.9302),
        840360470118: ('Queens-Jamaica', 'Queens County', 40.7014, -73.8156),
        
        # Bronx
        840360610135: ('Bronx-SW', 'Bronx County', 40.8298, -73.8850),
        840360610115: ('Bronx-Pelham', 'Bronx County', 40.8648, -73.8276),
        
        # Staten Island
        840360850055: ('Staten Island-Fresh Kills', 'Richmond County', 40.5834, -74.1677),
        840360850111: ('Staten Island-Coney Island', 'Richmond County', 40.5755, -74.1333),
        
        # Westchester County
        840360050080: ('Westchester-Yonkers', 'Westchester County', 40.9230, -73.8987),
        840360050110: ('Westchester-Mamaroneck', 'Westchester County', 40.9450, -73.7350),
        840360050112: ('Westchester-Croton', 'Westchester County', 41.1833, -73.8667),
        
        # New Jersey - Bergen & Hudson
        840360710002: ('NJ-Hudson', 'Hudson County', 40.7178, -74.0569),
        
        # Connecticut
        840090090027: ('CT-New Haven', 'New Haven County', 41.3083, -72.9279),
        840090110124: ('CT-Bridgeport', 'Fairfield County', 41.1833, -73.1833),
        840090011123: ('CT-Stamford', 'Fairfield County', 41.0534, -73.5387),
        
        # Long Island - Nassau & Suffolk
        840340030010: ('Nassau-NW', 'Nassau County', 40.8333, -73.6667),
        840340070010: ('Nassau-Central', 'Nassau County', 40.8500, -73.5000),
        840340170008: ('Suffolk-E', 'Suffolk County', 40.9500, -72.8000),
        840340171003: ('Suffolk-SE', 'Suffolk County', 40.8667, -72.7333),
        840340210005: ('Suffolk-Central', 'Suffolk County', 40.9000, -72.9000),
        840340210008: ('Suffolk-NE', 'Suffolk County', 41.0500, -72.7500),
        840340390004: ('Nassau-SW', 'Nassau County', 40.6833, -73.5000),
        840340392003: ('Nassau-S', 'Nassau County', 40.6500, -73.6667),
        840340190001: ('Hempstead', 'Nassau County', 40.7550, -73.6219),
        840340273001: ('Freeport', 'Nassau County', 40.6575, -73.5819),
        840340230011: ('Rockville Centre', 'Nassau County', 40.6667, -73.6500),
        840340410007: ('Valley Stream', 'Nassau County', 40.6650, -73.7100),
        
        # Rockland County, NY
        840360810120: ('Rockland-W', 'Rockland County', 41.0880, -74.2435),
        840360810124: ('Rockland-S', 'Rockland County', 41.1333, -74.0333),
        
        # Orange County, NY
        840360870005: ('Orange County', 'Orange County', 41.3333, -74.2667),
        
        # Dutchess & Putnam Counties, NY
        840361030009: ('Dutchess County', 'Dutchess County', 41.6333, -73.7000),
        840361192004: ('Putnam County', 'Putnam County', 41.4667, -73.8667),
    }
    
    sites_list = []
    for aqs_id in unique_aqs_ids:
        if aqs_id in aqs_mapping:
            site_name, county, lat, lon = aqs_mapping[aqs_id]
            sites_list.append({
                'aqs_id_full': aqs_id,
                'site_name': site_name,
                'county': county,
                'latitude': lat,
                'longitude': lon
            })
        else:
            # For unknown AQS IDs, create generic entry with NYC center coordinates
            sites_list.append({
                'aqs_id_full': aqs_id,
                'site_name': f'Location-{aqs_id}',
                'county': 'Other',
                'latitude': 40.7128,  # NYC center
                'longitude': -74.0060
            })
    
    sites = pd.DataFrame(sites_list)
    return sites

# ============================================================================
# HSRI CALCULATION (from project specification)
# ============================================================================
def compute_hsri(temp_f, humidity, wind_speed, solar_radiation, uv_index, cloud_cover):
    """
    Compute Heat Stress Risk Index (HSRI).
    
    Formula: HSRI = HI_base + α·UV + β·SR_eff − γ·WS [− δ·CC]
    
    where:
    - HI_base: NWS Heat Index computed from temperature and humidity
    - UV: UV index (0-10+), higher increases radiant heat load
    - SR_eff: Effective solar radiation (W/m²), scaled to ~0-1
    - WS: Wind speed (mph), cooling effect reduces HSRI
    - CC: Cloud cover (%), shading effect
    
    Calibrated weights: α=0.3, β=8, γ=4, δ=0.05
    Missing values for solar, UV, and cloud cover are treated as 0
    """
    # NWS Heat Index (Rothfusz regression)
    hi_base = compute_hi_nws(temp_f, humidity)
    
    # Handle missing values for solar radiation, UV, and cloud cover
    sr_eff = 0 if pd.isna(solar_radiation) else max(0, solar_radiation / 1000.0)
    uv_val = 0 if pd.isna(uv_index) else uv_index
    cc_val = 0 if pd.isna(cloud_cover) else cloud_cover
    
    # HSRI components with empirically calibrated weights
    alpha, beta, gamma, delta = 0.3, 8.0, 4.0, 0.05
    hsri = hi_base + alpha * uv_val + beta * sr_eff - gamma * wind_speed - delta * cc_val
    
    return np.clip(hsri, -100, 100)  # Reasonable bounds for human comfort index

def compute_hi_nws(temp_f, humidity):
    """NWS Heat Index (Rothfusz regression)."""
    T = temp_f
    RH = humidity
    
    if T < 80:
        return T
    
    # Coefficients
    c1, c2, c3 = -42.379, 2.04901523, 10.14333127
    c4, c5, c6 = -0.22475541, -0.00683783, -0.05481717
    c7, c8, c9 = 0.00122874, 0.00085282, -0.00000199
    
    HI = (c1 + c2*T + c3*RH + c4*T*RH + c5*T**2 + c6*RH**2 +
          c7*T**2*RH + c8*T*RH**2 + c9*T**2*RH**2)
    return HI

def forecast_hsri(historical_data, days_ahead=3):
    """
    Forecast HSRI for next 1-3 days using Linear Regression.
    
    Based on project findings: Linear Regression (R² = 0.965) recommended
    for operational deployment due to interpretability and accuracy.
    """
    if len(historical_data) < 10:
        return None
    
    try:
        # Prepare features for modeling
        feature_cols = ['temp', 'humidity', 'windspeed', 'solarradiation', 'uvindex', 'cloudcover']
        X = historical_data[feature_cols].copy()
        
        # Fill NaN values in solar, UV, and cloud cover with column mean
        X['solarradiation'] = X['solarradiation'].fillna(X['solarradiation'].mean())
        X['uvindex'] = X['uvindex'].fillna(X['uvindex'].mean())
        X['cloudcover'] = X['cloudcover'].fillna(X['cloudcover'].mean())
        
        X = X.values
        y = historical_data['hsri'].values
        
        # Train linear regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate forecast by interpolating future weather patterns
        avg_features = X.mean(axis=0)
        forecast_values = []
        
        for day in range(1, days_ahead + 1):
            # Simple trend: assume weather gradually changes
            forecast_features = avg_features * (1 + 0.02 * day)
            forecast_hsri = model.predict([forecast_features])[0]
            forecast_values.append(np.clip(forecast_hsri, -100, 100))
        
        return forecast_values
    except:
        return None

def get_risk_category(hsri):
    """Categorize heat risk based on HSRI threshold."""
    if hsri >= 85:
        return "🔴 CRITICAL", "Critical Heat"
    elif hsri >= 75:
        return "🟠 HIGH", "High Heat"
    elif hsri >= 65:
        return "🟡 MODERATE", "Moderate Heat"
    elif hsri >= 50:
        return "🟢 LOW", "Mild"
    elif hsri >= 30:
        return "🔵 COOL", "Cool"
    else:
        return "⚪ FREEZING", "Freezing"

# ============================================================================
# MAIN APP
# ============================================================================

# Load data
try:
    weather_df = load_weather_data()
except FileNotFoundError:
    st.error("❌ `weather.csv` not found in data/ folder.")
    st.stop()

sites_df = load_site_data(weather_df)
metro_df = load_metro_data()

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-critical { color: #d62728; font-weight: bold; }
    .risk-high { color: #ff7f0e; font-weight: bold; }
    .risk-moderate { color: #ffbb78; font-weight: bold; }
    .risk-low { color: #2ca02c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ====================================================================
# SIDEBAR CONTROLS
# ====================================================================
st.sidebar.header("⚙️ Dashboard Controls")

# Time selection - use date and time inputs instead of slider
col_date, col_time = st.sidebar.columns(2)

min_date = weather_df['datetime'].min().date()
max_date = weather_df['datetime'].max().date()

with col_date:
    selected_date = st.date_input(
        "📅 Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

with col_time:
    selected_hour = st.selectbox(
        "🕐 Hour (UTC)",
        options=range(0, 24),
        index=0,
        help="Select hour (0-23)"
    )

# Construct datetime
selected_datetime = datetime.combine(selected_date, datetime.min.time()).replace(hour=selected_hour)

# HSRI Risk Threshold - use number input instead of slider
hsri_threshold = st.sidebar.number_input(
    "🌡️ HSRI Risk Threshold",
    min_value=-100,
    max_value=100,
    value=65,
    step=5,
    help="Show locations with HSRI >= threshold"
)

# NYC Borough/Area selection - ONLY show areas that have data
st.sidebar.markdown("### 📍 NYC Area Selection")

# Get sites available for current time
available_times = weather_df['datetime'].unique()
if pd.Timestamp(selected_datetime).tz is None:
    selected_ts = pd.Timestamp(selected_datetime, tz='UTC')
else:
    selected_ts = pd.Timestamp(selected_datetime)

closest_time = min(available_times, key=lambda x: abs((x - selected_ts).total_seconds()))
df_time = weather_df[weather_df['datetime'] == closest_time].copy()
df_time = df_time.merge(sites_df, on='aqs_id_full', how='left')

# Get only known sites (not Location-XXXXX) that have data at this time
known_sites_available = df_time[~df_time['site_name'].str.contains('Location-', regex=False)]['site_name'].unique().tolist()

if not known_sites_available:
    # Fallback to all available sites
    known_sites_available = df_time['site_name'].unique().tolist()

# Create borough options ONLY with sites that exist in current data
nyc_areas = {'All Areas': known_sites_available}

predefined_areas = {
    'Manhattan': ['Manhattan-Midtown', 'Manhattan-Upper West', 'Manhattan-Upper East'],
    'Brooklyn': ['Brooklyn-Downtown'],
    'Queens': ['Queens-Astoria', 'Queens-Jamaica'],
    'Bronx': ['Bronx-SW', 'Bronx-Pelham'],
    'Staten Island': ['Staten Island-Fresh Kills', 'Staten Island-Coney Island'],
    'Westchester': ['Westchester-Yonkers', 'Westchester-Mamaroneck', 'Westchester-Croton'],
    'Long Island (Nassau)': ['Nassau-NW', 'Nassau-Central', 'Nassau-SW', 'Nassau-S', 'Hempstead', 'Freeport', 'Rockville Centre', 'Valley Stream'],
    'Long Island (Suffolk)': ['Suffolk-E', 'Suffolk-SE', 'Suffolk-Central', 'Suffolk-NE'],
    'New Jersey': ['NJ-Hudson'],
    'Connecticut': ['CT-New Haven', 'CT-Bridgeport', 'CT-Stamford'],
    'Rockland County': ['Rockland-W', 'Rockland-S'],
    'Orange/Dutchess': ['Orange County', 'Dutchess County', 'Putnam County']
}

for area_name, sites in predefined_areas.items():
    available_for_area = [s for s in sites if s in known_sites_available]
    if available_for_area:
        nyc_areas[area_name] = available_for_area

selected_area = st.sidebar.selectbox(
    "Select NYC Borough/Area",
    list(nyc_areas.keys()),
    help="Only shows areas with available data"
)

st.sidebar.divider()
st.sidebar.markdown("### 📊 Project Info")
st.sidebar.info("""
**Short-Term Heat Stress Forecasting**

Reduces heat-related hospital admissions by 20% through neighborhood-level predictions.

**Model:** Linear Regression (R² = 0.965)
**Update Frequency:** Hourly
**Coverage:** All Available Stations
""")

st.sidebar.info(f"📍 Data for: **{pd.Timestamp(closest_time).strftime('%Y-%m-%d %H:%M UTC')}**")

# ====================================================================
# CREATE TABS
# ====================================================================
tab_dashboard, tab_weather, tab_about = st.tabs(["📊 Dashboard", "🌦️ Weather Details", "ℹ️ About"])

# ====================================================================
# TAB 1: DASHBOARD
# ====================================================================
with tab_dashboard:
    
    df_current = df_time.copy()
    
    if not df_current.empty and len(df_current) > 0:
        # Compute HSRI for current snapshot
        df_current['hsri'] = df_current.apply(
            lambda row: compute_hsri(
                row.get('temp', 70),
                row.get('humidity', 50),
                row.get('windspeed', 5),
                row.get('solarradiation', 500),
                row.get('uvindex', 5),
                row.get('cloudcover', 50)
            ), axis=1
        )
        
        # Enrich with metro data if available
        if metro_df is not None:
            df_current = df_current.merge(
                metro_df, 
                left_on='county', 
                right_on='county', 
                how='left'
            )
        
        # Add risk categories
        if not df_current.empty and len(df_current) > 0:
            risk_data = df_current['hsri'].apply(lambda x: pd.Series(get_risk_category(x)))
            if risk_data.shape[1] >= 2:
                df_current['risk_emoji'] = risk_data.iloc[:, 0]
                df_current['risk_text'] = risk_data.iloc[:, 1]
            else:
                df_current['risk_emoji'] = 'N/A'
                df_current['risk_text'] = 'N/A'
        else:
            df_current['risk_emoji'] = 'N/A'
            df_current['risk_text'] = 'N/A'
        
        # Filter by selected area/borough
        selected_sites = nyc_areas[selected_area]
        df_area = df_current[df_current['site_name'].isin(selected_sites)].copy()
        
        if df_area.empty:
            df_area = df_current.copy()
        
        # Filter by HSRI threshold
        df_high_risk = df_area[df_area['hsri'] >= hsri_threshold].copy()
        
        # ====================================================================
        # ROW 1: KEY METRICS
        # ====================================================================
        st.header(f"Real-time Heat Stress Monitoring - {selected_area}")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            avg_hsri = df_area['hsri'].mean() if not df_area.empty else None
            if pd.notna(avg_hsri):
                st.metric("📊 Avg HSRI", f"{avg_hsri:.1f}°F")
            else:
                st.metric("📊 Avg HSRI", "N/A")
        
        with col2:
            max_hsri = df_area['hsri'].max() if not df_area.empty else None
            if pd.notna(max_hsri):
                risk_emoji, risk_text = get_risk_category(max_hsri)
                st.metric("🔥 Peak HSRI", f"{max_hsri:.1f}°F", delta=risk_text)
            else:
                st.metric("🔥 Peak HSRI", "N/A")
        
        with col3:
            high_risk_count = len(df_high_risk) if not df_high_risk.empty else 0
            st.metric("⚠️ High-Risk Sites", high_risk_count)
        
        with col4:
            avg_temp = df_area['temp'].mean() if 'temp' in df_area.columns and not df_area.empty else None
            if pd.notna(avg_temp):
                st.metric("🌡️ Avg Temp", f"{avg_temp:.1f}°F")
            else:
                st.metric("🌡️ Avg Temp", "N/A")
        
        with col5:
            avg_humidity = df_area['humidity'].mean() if 'humidity' in df_area.columns and not df_area.empty else None
            if pd.notna(avg_humidity):
                st.metric("💧 Avg Humidity", f"{avg_humidity:.0f}%")
            else:
                st.metric("💧 Avg Humidity", "N/A")
        
        st.divider()
        
        # ====================================================================
        # HSRI DISTRIBUTION & FORECAST
        # ====================================================================
        col_dist, col_forecast = st.columns(2)
        
        with col_dist:
            st.subheader("📈 HSRI Distribution")
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=df_current['hsri'],
                nbinsx=15,
                marker_color='#FF6B6B',
                name='HSRI',
                hovertemplate='HSRI Range: %{x}<br>Count: %{y}<extra></extra>'
            ))
            fig.add_vline(
                x=hsri_threshold, 
                line_dash="dash", 
                line_color="darkred", 
                line_width=2,
                annotation_text=f"Threshold: {hsri_threshold}",
                annotation_position="top right"
            )
            fig.update_layout(
                title="Distribution Across All Sites",
                xaxis_title="HSRI Value",
                yaxis_title="Number of Sites",
                height=400,
                template="plotly_white",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_forecast:
            st.subheader("🔮 3-Day HSRI Forecast")
            
            forecast = forecast_hsri(df_current, days_ahead=3)
            
            if forecast:
                forecast_dates = [closest_time + timedelta(days=i) for i in range(1, 4)]
                forecast_data = pd.DataFrame({
                    'Date': forecast_dates,
                    'Forecast HSRI': forecast
                })
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=forecast_data['Date'],
                    y=forecast_data['Forecast HSRI'],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=10)
                ))
                fig.add_hline(
                    y=hsri_threshold,
                    line_dash="dash",
                    line_color="darkred",
                    annotation_text=f"Threshold: {hsri_threshold}"
                )
                fig.update_layout(
                    title="Next 3 Days",
                    xaxis_title="Date",
                    yaxis_title="Predicted HSRI",
                    height=400,
                    template="plotly_white",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Insufficient data for forecasting")
        
        st.divider()
        
        # ====================================================================
        # OPERATIONAL INSIGHTS
        # ====================================================================
        st.subheader("💡 Operational Insights")
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            pct_high_risk = (len(df_high_risk) / len(df_current) * 100) if len(df_current) > 0 else 0
            st.metric("🏢 Cooling Centers to Activate", f"{len(df_high_risk)} of {len(df_current)}", 
                     delta=f"{pct_high_risk:.1f}%")
            st.caption("Estimated cost savings: 40% reduction from reactive approach")
        
        with insight_col2:
            if not df_high_risk.empty and 'county' in df_high_risk.columns:
                top_county = df_high_risk['county'].value_counts().idxmax()
                st.metric("📍 Most Affected County", top_county)
                st.caption(f"{len(df_high_risk[df_high_risk['county']==top_county])} sites at high risk")
            else:
                st.metric("📍 Most Affected County", "N/A")
        
        with insight_col3:
            if max_hsri >= 75:
                st.metric("🏥 Healthcare Alert", "HIGH ⚠️")
                st.caption("Expect potential increase in heat-related ED visits")
            else:
                st.metric("🏥 Healthcare Alert", "LOW ✅")
                st.caption("Normal operations expected")
        
        st.divider()
        
        # ====================================================================
        # MAP ON DASHBOARD
        # ====================================================================
        st.subheader("🗺️ Geographic Heat Risk Map")
        
        # Create Folium map
        if not df_area.empty:
            center_lat = df_area['latitude'].mean()
            center_lon = df_area['longitude'].mean()
        else:
            center_lat = 40.7128
            center_lon = -74.0060
        
        if pd.isna(center_lat) or pd.isna(center_lon):
            center_lat = 40.7128
            center_lon = -74.0060
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        def get_marker_color(hsri_val):
            if hsri_val >= 85:
                return '#d62728'  # Critical - dark red
            elif hsri_val >= 75:
                return '#ff7f0e'  # High - orange
            elif hsri_val >= 65:
                return '#ffbb78'  # Moderate - light orange
            elif hsri_val >= 50:
                return '#2ca02c'  # Low - green
            elif hsri_val >= 30:
                return '#1f77b4'  # Cool - blue
            else:
                return '#6a0dad'  # Freezing - dark purple
        
        for _, row in df_area.iterrows():
            hsri_val = row.get('hsri', 0)
            site_name = row.get('site_name', 'Unknown')
            temp_val = row.get('temp', 'N/A')
            humidity_val = row.get('humidity', 'N/A')
            wind_val = row.get('windspeed', 'N/A')
            county = row.get('county', 'Unknown')
            
            risk_emoji, risk_text = get_risk_category(hsri_val)
            
            popup_text = f"""
            <div style="font-family: Arial; width: 300px;">
                <b style="font-size: 14px;">{site_name}</b><br/>
                <hr style="margin: 5px 0;">
                <b>County:</b> {county}<br/>
                <b>🌡️ Temperature:</b> {temp_val:.1f}°F<br/>
                <b>💧 Humidity:</b> {humidity_val:.0f}%<br/>
                <b>💨 Wind Speed:</b> {wind_val:.1f} mph<br/>
                <hr style="margin: 5px 0;">
                <b style="font-size: 13px;">HSRI: {hsri_val:.1f}</b><br/>
                <b>{risk_emoji} {risk_text}</b>
            </div>
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=16,
                popup=folium.Popup(popup_text, max_width="300px"),
                tooltip=f"{site_name}: HSRI {hsri_val:.1f}",
                color=get_marker_color(hsri_val),
                fill=True,
                fillColor=get_marker_color(hsri_val),
                fillOpacity=0.7,
                weight=2
            ).add_to(m)
            
            # Add text label with HSRI value inside circle
            # Use darker text for light backgrounds (Moderate/Low levels)
            text_color = '#333333' if 50 <= hsri_val < 75 else 'white'
            text_shadow = '1px 1px 2px rgba(255,255,255,0.8)' if 50 <= hsri_val < 75 else '1px 1px 2px rgba(0,0,0,0.8)'
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                icon=folium.DivIcon(html=f"""
                    <div style="
                        font-size: 13px;
                        font-weight: bold;
                        color: {text_color};
                        text-align: center;
                        text-shadow: {text_shadow};
                        width: 32px;
                        height: 32px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-left: -16px;
                        margin-top: -16px;
                    ">{hsri_val:.0f}</div>
                """)
            ).add_to(m)
        
        st_folium(m, width=1400, height=700)
        
        # Legend with Clothing Recommendations
        st.markdown("**👕 Risk Level Legend with Protective Clothing Guide**")
        
        recommendations = [
            ("85+", "🩳", "Shorts + Tank", "🔴 Critical", "#ffe6e6", "#d62728"),
            ("75-84", "👕", "Shorts + T-Shirt", "🟠 High", "#fff0e6", "#ff7f0e"),
            ("65-74", "👔", "Short Sleeves", "🟡 Moderate", "#fffef0", "#ffbb78"),
            ("50-64", "👗", "Light Layers", "🟢 Low", "#f0fff0", "#2ca02c"),
            ("30-49", "🧥", "Light Jacket", "🔵 Cool", "#f0f8ff", "#1f77b4"),
            ("<30", "🧤", "Winter Coat", "🟣 Freezing", "#f3e6ff", "#6a0dad"),
        ]
        
        cols = st.columns(len(recommendations))
        for i, (hsri_range, clothing_emoji, clothing_desc, risk_label, bg_color, border_color) in enumerate(recommendations):
            with cols[i]:
                st.markdown(f"""
                <div style="padding: 12px; background-color: {bg_color}; border-left: 5px solid {border_color}; border-radius: 5px;">
                    <b>{risk_label}</b><br/>
                    <b>HSRI {hsri_range}</b><br/>
                    <div style="font-size: 28px; margin: 8px 0;">{clothing_emoji}</div>
                    <small>{clothing_desc}</small>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.warning(f"⚠️ No data available for {selected_datetime.strftime('%Y-%m-%d %H:%M UTC')}. Please select a different time.")

# ====================================================================
# TAB 2: WEATHER DETAILS
# ====================================================================
with tab_weather:
    
    if not df_current.empty and len(df_current) > 0:
        st.subheader("🌦️ Complete Weather Conditions by Site")
        st.markdown("Detailed weather variables and HSRI output for each location")
        
        for _, row in df_area.iterrows():
            site_name = row.get('site_name', 'Unknown')
            hsri_val = row.get('hsri', 0)
            risk_emoji, risk_text = get_risk_category(hsri_val)
            
            with st.expander(f"{risk_emoji} {site_name} - HSRI: {hsri_val:.1f}°F"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("**Temperature & Humidity**")
                    st.metric("🌡️ Temperature", f"{row.get('temp', 'N/A'):.1f}°F")
                    st.metric("💧 Humidity", f"{row.get('humidity', 'N/A'):.0f}%")
                
                with col2:
                    st.markdown("**Wind & Clouds**")
                    st.metric("💨 Wind Speed", f"{row.get('windspeed', 'N/A'):.1f} mph")
                    cc_val = row.get('cloudcover', 'N/A')
                    cc_display = "N/A" if pd.isna(cc_val) else f"{cc_val:.0f}%"
                    st.metric("☁️ Cloud Cover", cc_display)
                
                with col3:
                    st.markdown("**Solar & UV**")
                    sr_val = row.get('solarradiation', 'N/A')
                    sr_display = "N/A" if pd.isna(sr_val) else f"{sr_val:.0f} W/m²"
                    st.metric("☀️ Solar Radiation", sr_display)
                    
                    uv_val = row.get('uvindex', 'N/A')
                    uv_display = "N/A" if pd.isna(uv_val) else f"{uv_val:.1f}"
                    st.metric("🌫️ UV Index", uv_display)
                
                with col4:
                    st.markdown("**Heat Stress Index**")
                    st.metric("📊 HSRI Output", f"{hsri_val:.1f}°F")
                    st.metric("📍 County", row.get('county', 'N/A'))
                    st.caption(f"Updated: {closest_time.strftime('%H:%M UTC')}")
        
        # Data table
        st.subheader("📋 High-Risk Location Details")
        
        if not df_high_risk.empty:
            display_cols = ['site_name', 'county', 'temp', 'humidity', 'windspeed', 
                           'solarradiation', 'uvindex', 'cloudcover', 'hsri', 'risk_text']
            df_table = df_high_risk[[col for col in display_cols if col in df_high_risk.columns]].copy()
            
            df_table = df_table.rename(columns={
                'site_name': 'Site',
                'county': 'County',
                'temp': 'Temp (°F)',
                'humidity': 'Humidity (%)',
                'windspeed': 'Wind (mph)',
                'solarradiation': 'Solar (W/m²)',
                'uvindex': 'UV Index',
                'cloudcover': 'Cloud (%)',
                'hsri': 'HSRI',
                'risk_text': 'Risk Level'
            })
            
            st.dataframe(df_table, use_container_width=True, hide_index=True)
        else:
            st.info(f"✅ No sites exceed HSRI threshold of {hsri_threshold}")

# ====================================================================
# TAB 4: ABOUT
# ====================================================================
with tab_about:
    st.markdown("""
    # About This Dashboard
    
    ## Project Overview
    This Heat Stress Risk Index (HSRI) Weather Dashboard is a real-time monitoring and forecasting system 
    designed to reduce heat-related health impacts across the NYC metropolitan region. Developed as part of 
    Cornell University's SYSEN 5300 course, this project demonstrates predictive analytics for public health resilience.
    
    ### Project Goals
    - **Reduce hospital admissions** by 20% through early warning and targeted interventions
    - **Lower healthcare costs** by 40% via proactive cooling center placement and resource allocation
    - **Improve equity** by providing neighborhood-level forecasts for vulnerable populations
    - **Enable data-driven decision-making** for city planners, public health officials, and emergency managers
    
    ---
    
    ## How It Works
    
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
    - 🔴 **Critical** (≥85): Extreme danger - activate all emergency protocols
    - 🟠 **High** (≥75): Significant risk - increase cooling center capacity
    - 🟡 **Moderate** (≥65): Moderate risk - monitor vulnerable populations
    - 🟢 **Low** (≥50): Mild conditions - routine operations
    - 🔵 **Cool** (<50): Cool conditions - normal operations
    
    ---
    
    ## Data & Model
    
    ### Data Source
    - **Weather Data**: Hourly observations from 56 AQS (Air Quality System) monitoring stations
    - **Geographic Coverage**: NYC metro region including 5 NYC boroughs, Westchester County, surrounding NJ areas, and CT
    - **Time Period**: 2018-01-01 to 2025-06-01 (continuous hourly records)
    - **Variables**: Temperature, humidity, wind speed, solar radiation, UV index, cloud cover
    
    ### Forecasting Model
    - **Algorithm**: Linear Regression
    - **Model Accuracy**: R² = 0.965, RMSE = 3.0°F, MAE = 2.19°F
    - **Horizon**: 1-3 day advance forecasts
    - **Rationale**: Prioritizes interpretability and operational feasibility over black-box approaches
    
    ### Data Quality
    - ✓ Core meteorological parameters required (temp, humidity, windspeed)
    - ✓ Hourly temporal resolution for real-time monitoring
    - ✓ Multi-station coverage for geographic accuracy
    - ✓ Solar, UV, cloud data optional (shows "N/A" when unavailable)
    - ✓ Historical data spanning 2018-2025
    
    ---
    
    ## Key Features
    
    ### 📊 Dashboard Tab
    - Real-time HSRI metrics (average, peak, distribution)
    - Borough/area filtering for localized analysis
    - 3-day HSRI forecast with uncertainty
    - Operational insights (cooling center readiness, healthcare alert levels)
    - Protective clothing recommendations by risk level
    
    ### 🗺️ Large Map Tab
    - Interactive geographic map with color-coded risk markers
    - Click markers to view detailed conditions at each station
    - Zoom and pan to explore specific regions
    - Full-screen display for decision-making dashboards
    
    ### 🌦️ Weather Details Tab
    - Expandable detailed weather for each location
    - All 6 meteorological variables with units
    - HSRI output and risk categorization
    - High-risk location data table with filtering
    
    ### ℹ️ About Tab
    - Project background and goals
    - Technical documentation
    - Model performance metrics
    - How to interpret results
    
    ---
    
    ## Controls
    
    ### Dashboard Controls (Sidebar)
    - **Date Selector**: Choose observation date
    - **Hour Selector**: Select specific hour (UTC)
    - **HSRI Threshold**: Filter for high-risk locations
    - **Borough/Area**: View specific geographic regions
    - **3-Day Forecast**: Toggle predictive component
    
    ### Data Available
    - **Temporal Coverage**: 2018 to present (with historical data)
    - **Geographic Regions**: All NYC metro areas with active monitoring
    - **Borough Options**: Only shows areas with data at selected time
    
    ---
    
    ## Interpretation Guide
    
    ### For Public Health Officials
    - Monitor **Peak HSRI** to trigger emergency response protocols
    - Use **High-Risk Sites** count to allocate cooling center resources
    - Review **Most Affected County** for targeted interventions
    - Check **Healthcare Alert Level** to prepare ED capacity
    
    ### For City Planners
    - Use **3-Day Forecast** for advance planning
    - Identify chronically vulnerable areas through **HSRI Distribution**
    - Plan tree canopy and green space using **Solar Radiation** data
    - Consider wind corridors for natural cooling
    
    ### For Residents
    - Follow **Protective Clothing Guide** recommendations
    - Monitor **Peak HSRI** for personal outdoor activity planning
    - Check **Forecast** to prepare for future heat stress conditions
    - Know your nearest **Cooling Center** (via separate resource maps)
    
    ---
    
    ## Technical Details
    
    ### Data Processing
    1. Load hourly weather observations from CSV
    2. Filter for complete records (all 6 variables present)
    3. Map AQS IDs to geographic locations and counties
    4. Compute HSRI for each observation
    5. Categorize risk levels
    6. Generate forecasts using historical trends
    
    ### Map Visualization
    - Folium.js for interactive mapping
    - Color-coded circle markers for HSRI values
    - Popup information cards with all variables
    - Responsive zoom and pan controls
    
    ### Forecasting
    - Linear regression on 6-dimensional weather feature space
    - Trained on historical HSRI data
    - Future predictions based on trend extrapolation
    - Bounds: [-100, 100]°F to allow natural winter and summer values
    
    ---
    
    ## Project Team
    - **Institution**: Cornell University, College of Engineering (Systems Engineering)
    - **Course**: SYSEN 5300 - Systems Engineering and Six Sigma for the Design and Operation of Reliable Systems
    - **Academic Year**: Fall 2025
    
    ### Application Stack
    - **Frontend**: Streamlit (Python web app framework)
    - **Data Processing**: Pandas, NumPy
    - **Visualization**: Plotly, Folium
    - **Machine Learning**: scikit-learn
    - **Deployment**: Cloud-ready for Streamlit Community Cloud
    
    ---
    
    ## Further Information
    
    ### Related Resources
    - [Weather - Tim fraser - GitHub](https://github.com/timothyfraser/sts/tree/3week/data/weather)       
    - [NWS Heat Index](https://www.weather.gov/media/epz/wxcalc/heatIndex.pdf)
    - [EPA UV Index Guide](https://www.epa.gov/sites/production/files/2015-09/documents/UV_Index_10.pdf)
    - [CDC Heat Stress Prevention](https://www.cdc.gov/niosh/topics/emres/cheathstress.html)
    - [NYC Office of Emergency Management](https://www1.nyc.gov/site/em/index.page)
    
    ### Data Licensing
    - Weather data sourced from EPA AQS (public domain)
    - County geographic data from U.S. Census (public domain)
    
    ---
    
    *Last Updated: December 2025*
    """)

# ====================================================================
# FOOTER
# ====================================================================
st.divider()

col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.caption("📊 **Data Source:** NYC Metro AQS Network")
    st.caption(f"🔄 Last Update: {closest_time.strftime('%Y-%m-%d %H:%M UTC')}")

with col_footer2:
    st.caption("**Model Accuracy:** R² = 0.965, RMSE = 3.0°F")
    st.caption("**Project:** SYSEN 5300 • Cornell University")

with col_footer3:
    st.caption("**Formula:** HSRI = HI + 0.3·UV + 8·SR - 4·WS - 0.05·CC")
    st.caption("**Coverage:** All Available Stations • Hourly Updates")
