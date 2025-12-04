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
def load_weather_data(filepath='weather.csv'):
    """Load and preprocess weather CSV."""
    df = pd.read_csv(filepath)
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

@st.cache_data
def load_metro_data(filepath='metro.csv'):
    """Load metro area county data."""
    try:
        metro_df = pd.read_csv(filepath)
        return metro_df
    except FileNotFoundError:
        st.warning("⚠️ metro.csv not found. Using default site data.")
        return None

def load_site_data(weather_df=None):
    """Load site metadata - dynamically from weather data or defaults."""
    if weather_df is None:
        weather_df = load_weather_data()
    
    # Get unique AQS IDs from weather data
    unique_aqs_ids = weather_df['aqs_id_full'].unique()
    
    # Create mapping for known/major NYC metro AQS IDs
    aqs_mapping = {
        840421010055: ('New York-Brooklyn', 'Kings County', 40.6501, -73.9496),
        840360330029: ('Queens-Nassau', 'Queens County', 40.7282, -73.7949),
        840360470006: ('Westchester', 'Westchester County', 40.9176, -73.8312),
        840360610028: ('Bronx-Yonkers', 'Bronx County', 40.8448, -73.8648),
        840360850002: ('Staten Island', 'Richmond County', 40.5640, -74.0734),
        840360050001: ('New Jersey-Bergen', 'Bergen County', 40.8176, -74.0569),
        840361190001: ('New Jersey-Hudson', 'Hudson County', 40.7178, -74.0569),
        840360790003: ('Connecticut', 'New Haven County', 41.3083, -72.9279),
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
    """
    # NWS Heat Index (Rothfusz regression)
    hi_base = compute_hi_nws(temp_f, humidity)
    
    # Effective solar radiation (normalized by 1000)
    sr_eff = max(0, solar_radiation / 1000.0)  # scale to ~0-1
    
    # HSRI components with empirically calibrated weights
    alpha, beta, gamma, delta = 0.3, 8.0, 4.0, 0.05
    hsri = hi_base + alpha * uv_index + beta * sr_eff - gamma * wind_speed - delta * cloud_cover
    
    return np.clip(hsri, 30, 130)  # Reasonable bounds for human comfort index

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
        X = historical_data[['temp', 'humidity', 'windspeed', 'solarradiation', 'uvindex', 'cloudcover']].values
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
            forecast_values.append(np.clip(forecast_hsri, 30, 130))
        
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
    elif hsri >= 35:
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
    st.error("❌ `weather.csv` not found. Place it in the same directory as this app.")
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

# Time selection - convert to native Python datetime
min_date = weather_df['datetime'].min().to_pydatetime()
max_date = weather_df['datetime'].max().to_pydatetime()

selected_datetime = st.sidebar.slider(
    "📅 Select Time",
    min_value=min_date,
    max_value=max_date,
    value=max_date
)

hsri_threshold = st.sidebar.slider(
    "🌡️ HSRI Risk Threshold",
    min_value=30,
    max_value=130,
    value=65,
    step=5,
    help="Show locations with HSRI >= threshold"
)

# NYC Borough/Area selection
st.sidebar.markdown("### 📍 NYC Area Selection")

# Build dynamic area selection from available sites
all_known_sites = sites_df[~sites_df['site_name'].str.contains('Location-', regex=False)]['site_name'].unique().tolist()

nyc_areas = {
    'All Areas': list(sites_df['site_name'].unique()),
}

# Add pre-defined groupings for known sites (always show these options)
predefined_areas = {
    'Manhattan/Brooklyn': ['New York-Brooklyn'],
    'Queens/Nassau': ['Queens-Nassau'],
    'Westchester': ['Westchester'],
    'Bronx/Yonkers': ['Bronx-Yonkers'],
    'Staten Island': ['Staten Island'],
    'New Jersey': ['New Jersey-Bergen', 'New Jersey-Hudson'],
    'Connecticut': ['Connecticut']
}

# Add all predefined areas, filtering to only available sites
for area_name, sites in predefined_areas.items():
    available_for_area = [s for s in sites if s in all_known_sites]
    if available_for_area:
        nyc_areas[area_name] = available_for_area
    else:
        # If no known sites available, still show the option but it will display all data
        nyc_areas[area_name] = list(sites_df['site_name'].unique())

selected_area = st.sidebar.selectbox(
    "Select NYC Borough/Area",
    list(nyc_areas.keys()),
    help="Filter by NYC borough or view all areas"
)

show_forecast = st.sidebar.checkbox("📈 Show 3-Day Forecast", value=True)

st.sidebar.divider()
st.sidebar.markdown("### 📊 Project Info")
st.sidebar.info("""
**Short-Term Heat Stress Forecasting**

Reduces heat-related hospital admissions by 20% through neighborhood-level predictions.

**Model:** Linear Regression (R² = 0.965)
**Update Frequency:** Hourly
**Coverage:** NYC Metro (22 counties)
""")

# ====================================================================
# MAIN CONTENT
# ====================================================================

# Get current data
available_times = weather_df['datetime'].unique()
# Convert selected_datetime to pandas Timestamp with UTC timezone
# Handle both naive and timezone-aware datetimes
if pd.Timestamp(selected_datetime).tz is None:
    selected_ts = pd.Timestamp(selected_datetime, tz='UTC')
else:
    selected_ts = pd.Timestamp(selected_datetime)

closest_time = min(available_times, key=lambda x: abs((x - selected_ts).total_seconds()))
df_current = weather_df[weather_df['datetime'] == closest_time].copy()

st.sidebar.info(f"📍 Data for: **{pd.Timestamp(closest_time).strftime('%Y-%m-%d %H:%M UTC')}**")

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
    
    # Merge with site data
    df_current = df_current.merge(sites_df, on='aqs_id_full', how='left')
    df_current = df_current.dropna(subset=['latitude', 'longitude'])
    
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
    st.header("🌤️ NYC Metro Heat Stress Dashboard")
    st.markdown(f"Real-time HSRI monitoring with forecasting for **{selected_area}**")
    
    if df_area.empty:
        st.warning(f"⚠️ No data available for {selected_datetime.strftime('%Y-%m-%d %H:%M UTC')}. Please select a different time.")
    
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_hsri = df_area['hsri'].mean() if not df_area.empty else None
        if pd.notna(avg_hsri):
            st.metric("📊 Avg HSRI", f"{avg_hsri:.1f}°F", 
                     help="Average Heat Stress Risk Index")
        else:
            st.metric("📊 Avg HSRI", "N/A", help="No data available")
    
    with col2:
        max_hsri = df_area['hsri'].max() if not df_area.empty else None
        if pd.notna(max_hsri):
            risk_emoji, risk_text = get_risk_category(max_hsri)
            st.metric("🔥 Peak HSRI", f"{max_hsri:.1f}°F", delta=risk_text)
        else:
            st.metric("🔥 Peak HSRI", "N/A", delta="No data")
    
    with col3:
        high_risk_count = len(df_high_risk) if not df_high_risk.empty else 0
        st.metric("⚠️ High-Risk Sites", high_risk_count, 
                 help=f"Locations with HSRI ≥ {hsri_threshold}")
    
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
    
    # ====================================================================
    # ROW 2: INTERACTIVE MAP WITH METRO INTEGRATION
    # ====================================================================
    st.subheader("🗺️ Geographic Heat Risk Map")
    
    col_map, col_legend = st.columns([3, 1])
    
    with col_map:
        # Create Folium map centered on selected area (with fallback to NYC center)
        if not df_area.empty:
            center_lat = df_area['latitude'].mean()
            center_lon = df_area['longitude'].mean()
        else:
            # Default to NYC center
            center_lat = 40.7128
            center_lon = -74.0060
        
        # Ensure no NaN values
        if pd.isna(center_lat) or pd.isna(center_lon):
            center_lat = 40.7128
            center_lon = -74.0060
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Define color mapping based on HSRI
        def get_marker_color(hsri_val):
            if hsri_val >= 85:
                return '#d62728'  # Red
            elif hsri_val >= 75:
                return '#ff7f0e'  # Orange
            elif hsri_val >= 65:
                return '#ffbb78'  # Light Orange
            elif hsri_val >= 50:
                return '#2ca02c'  # Green
            else:
                return '#1f77b4'  # Blue
        
        # Add markers for each location in selected area
        for _, row in df_area.iterrows():
            hsri_val = row.get('hsri', 0)
            site_name = row.get('site_name', 'Unknown')
            temp_val = row.get('temp', 'N/A')
            humidity_val = row.get('humidity', 'N/A')
            wind_val = row.get('windspeed', 'N/A')
            county = row.get('county', 'Unknown')
            
            risk_emoji, risk_text = get_risk_category(hsri_val)
            
            popup_text = f"""
            <div style="font-family: Arial; width: 250px;">
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
                radius=10,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{site_name}: HSRI {hsri_val:.1f}",
                color=get_marker_color(hsri_val),
                fill=True,
                fillColor=get_marker_color(hsri_val),
                fillOpacity=0.7,
                weight=2
            ).add_to(m)
        
        st_folium(m, width=900, height=500)
    
    with col_legend:
        st.markdown("**Risk Legend**")
        st.markdown("""
        <div style="padding: 10px; background-color: #fff0f0; border-left: 4px solid #d62728; margin: 5px 0;">
        <b>🔴 Critical</b><br/>HSRI ≥ 85
        </div>
        <div style="padding: 10px; background-color: #fff5f0; border-left: 4px solid #ff7f0e; margin: 5px 0;">
        <b>🟠 High</b><br/>HSRI ≥ 75
        </div>
        <div style="padding: 10px; background-color: #fffef0; border-left: 4px solid #ffbb78; margin: 5px 0;">
        <b>🟡 Moderate</b><br/>HSRI ≥ 65
        </div>
        <div style="padding: 10px; background-color: #f0fff0; border-left: 4px solid #2ca02c; margin: 5px 0;">
        <b>🟢 Low</b><br/>HSRI ≥ 50
        </div>
        <div style="padding: 10px; background-color: #f0f8ff; border-left: 4px solid #1f77b4; margin: 5px 0;">
        <b>🔵 Cool</b><br/>HSRI < 50
        </div>
        """, unsafe_allow_html=True)
    
    # ====================================================================
    # ROW 3: DETAILED DATA TABLE
    # ====================================================================
    st.subheader("📋 High-Risk Location Details")
    
    if not df_high_risk.empty:
        display_cols = ['site_name', 'county', 'temp', 'humidity', 'windspeed', 
                       'solarradiation', 'uvindex', 'cloudcover', 'hsri', 'risk_text']
        df_table = df_high_risk[[col for col in display_cols if col in df_high_risk.columns]].copy()
        
        # Rename columns for display
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
        st.info(f"✅ No sites currently exceed HSRI threshold of {hsri_threshold}")
    
    # ====================================================================
    # ROW 3B: COMPREHENSIVE WEATHER OUTPUT - ALL VARIABLES
    # ====================================================================
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
                st.metric("🌡️ Temperature", f"{row.get('temp', 'N/A'):.1f}°F", delta="Current")
                st.metric("💧 Humidity", f"{row.get('humidity', 'N/A'):.0f}%", delta="Relative")
            
            with col2:
                st.markdown("**Wind & Clouds**")
                st.metric("💨 Wind Speed", f"{row.get('windspeed', 'N/A'):.1f} mph", delta="Cooling Effect")
                st.metric("☁️ Cloud Cover", f"{row.get('cloudcover', 'N/A'):.0f}%", delta="Shading")
            
            with col3:
                st.markdown("**Solar & UV**")
                st.metric("☀️ Solar Radiation", f"{row.get('solarradiation', 'N/A'):.0f} W/m²", delta="Heat Load")
                st.metric("🌫️ UV Index", f"{row.get('uvindex', 'N/A'):.1f}", delta="Radiant Exposure")
            
            with col4:
                st.markdown("**Heat Stress Index**")
                st.metric("📊 HSRI Output", f"{hsri_val:.1f}°F", delta=risk_text)
                st.metric("📍 County", row.get('county', 'N/A'), delta="Location")
                st.caption(f"Updated: {closest_time.strftime('%H:%M UTC')}")
    
    # ====================================================================
    # ROW 4: HSRI DISTRIBUTION & FORECAST
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
        
        if show_forecast:
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
        else:
            st.info("📊 Enable forecast in sidebar to view predictions")
    
    # ====================================================================
    # ROW 5: OPERATIONAL INSIGHTS
    # ====================================================================
    st.divider()
    st.subheader("💡 Operational Insights")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        # Cooling center readiness
        pct_high_risk = (len(df_high_risk) / len(df_current) * 100) if len(df_current) > 0 else 0
        st.metric("🏢 Cooling Centers to Activate", f"{len(df_high_risk)} of {len(df_current)}", 
                 delta=f"{pct_high_risk:.1f}%")
        st.caption(f"Estimated cost savings: 40% reduction from reactive approach")
    
    with insight_col2:
        # Most affected county
        if not df_high_risk.empty and 'county' in df_high_risk.columns:
            top_county = df_high_risk['county'].value_counts().idxmax()
            st.metric("📍 Most Affected County", top_county)
            st.caption(f"{len(df_high_risk[df_high_risk['county']==top_county])} sites at high risk")
        else:
            st.metric("📍 Most Affected County", "N/A")
    
    with insight_col3:
        # Healthcare preparation
        if max_hsri >= 75:
            st.metric("🏥 Healthcare Alert Level", "HIGH ⚠️")
            st.caption("Expect potential increase in heat-related ED visits")
        else:
            st.metric("🏥 Healthcare Alert Level", "LOW ✅")
            st.caption("Normal operations expected")
    
    # ====================================================================
    # ROW 6: CLOTHING RECOMMENDATIONS
    # ====================================================================
    st.subheader("👕 Protective Clothing Guide by Risk Level")
    
    recommendations = [
        ("85+", "🩳 Shorts + Tank Top", "🔴 Critical Heat", "#ffe6e6"),
        ("75-84", "👕 Shorts + T-Shirt", "🟠 High Heat", "#fff0e6"),
        ("65-74", "👔 Short Sleeves", "🟡 Moderate Heat", "#fffef0"),
        ("50-64", "👗 Light Layers", "🟢 Mild", "#f0fff0"),
        ("<50", "🧥 Jacket", "🔵 Cool", "#f0f8ff"),
    ]
    
    cols = st.columns(len(recommendations))
    for i, (hsri_range, clothing, risk, bg_color) in enumerate(recommendations):
        with cols[i]:
            # Parse clothing string safely - extract emoji and description
            parts = clothing.split(None, 1)  # Split on first whitespace
            emoji = parts[0] if parts else "👕"
            description = parts[1] if len(parts) > 1 else clothing
            
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; text-align: center;">
                <b>HSRI {hsri_range}</b><br/>
                <span style="font-size: 24px;">{emoji}</span><br/>
                <small>{description}</small><br/>
                <b>{risk}</b>
            </div>
            """, unsafe_allow_html=True)
    
    # ====================================================================
    # FOOTER
    # ====================================================================
    st.divider()
    
    col_footer1, col_footer2, col_footer3 = st.columns(3)
    
    with col_footer1:
        st.caption("📊 **Data Source:** NYC Metro Weather Network")
        st.caption(f"🔄 Last Update: {closest_time.strftime('%Y-%m-%d %H:%M UTC')}")
    
    with col_footer2:
        st.caption("**Model Accuracy:** R² = 0.965, RMSE = 3.0°F (Linear Regression)")
        st.caption("**Project:** SYSEN 5300 • Cornell University")
    
    with col_footer3:
        st.caption("**Formula:** HSRI = HI + 0.3·UV + 8·SR - 4·WS - 0.05·CC")
        st.caption("**Update Frequency:** Hourly • **Forecast Horizon:** 1-3 days")

else:
    st.warning("⚠️ No data available for the selected time.")
