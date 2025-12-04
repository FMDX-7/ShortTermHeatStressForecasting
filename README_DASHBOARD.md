# 🌤️ NYC Metro HSRI Weather Dashboard

An interactive Streamlit app that displays **Heat Stress Risk Index (HSRI)** and real-time weather conditions across New York City metro region with clothing recommendations.

## Features

✅ **Interactive Map** — Apple Weather-style map with color-coded HSRI markers  
✅ **Real-time HSRI** — Computed from temp, humidity, wind, solar radiation, UV  
✅ **Clothing Recommendations** — Automatic suggestions (shorts → winter gear)  
✅ **Time Slider** — Explore historical or near-real-time data  
✅ **HSRI Threshold Filter** — Show only locations above a certain risk level  
✅ **Summary Metrics** — Avg HSRI, max HSRI, location counts  
✅ **Data Table** — Detailed view of all sites  
✅ **Distribution Chart** — Histogram of HSRI across all sites  

## Installation (Local)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run app.py
   ```

3. **Place `weather.csv` in the same directory** as `app.py`.

4. Open your browser to `http://localhost:8501`

## Deployment to Streamlit Cloud

1. **Push your code to GitHub** (create a repo with `app.py`, `requirements.txt`, `weather.csv`):
   ```bash
   git add app.py requirements.txt weather.csv .gitignore
   git commit -m "Initial HSRI dashboard"
   git push origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**
   - Click "New app"
   - Connect your GitHub repo
   - Select branch, file path (`app.py`)
   - Deploy!

3. **Your app will be live at:** `https://share.streamlit.io/YOUR_USERNAME/YOUR_REPO/app.py`

## HSRI Formula

```
HSRI = HI_base + α·UV + β·SR_eff − γ·WS − δ·CC

where:
  HI_base  = NWS Heat Index (Rothfusz regression)
  α = 0.3  (UV coefficient)
  β = 8.0  (Solar radiation coefficient)
  γ = 4.0  (Wind speed coefficient, reduces stress)
  δ = 0.05 (Cloud cover coefficient, slight reduction)
```

## Data Sources

- **weather.csv** — Hourly weather from Visual Crossing API (NYC metro region)
- **sites.csv** (generated) — Air quality sensor locations with lat/lon

## File Structure

```
project/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── weather.csv         # Hourly weather data
├── README.md           # This file
└── .gitignore          # Exclude large files from git
```

## Customization

### Change HSRI coefficients:
Edit the `compute_hsri()` function in `app.py` to adjust `alpha`, `beta`, `gamma`, `delta`.

### Add more sites:
Update the `load_site_data()` function or link to an external `sites.csv`.

### Change map tiles:
In the Folium section, replace `'OpenStreetMap'` with:
- `'CartoDB positron'` (light theme)
- `'CartoDB positron_no_labels'` (minimal)
- `'Stamen Terrain'` (topographic)

## Troubleshooting

**"weather.csv not found"**  
→ Ensure `weather.csv` is in the same folder as `app.py`.

**Map doesn't load**  
→ Check internet connection; `streamlit-folium` requires Folium backend access.

**Slow performance on large datasets**  
→ Use `@st.cache_data` decorators to cache expensive computations.

---

**Author:** Six Sigma Project Team  
**Developed:** December 2025  
**Last Updated:** 2025-12-04
