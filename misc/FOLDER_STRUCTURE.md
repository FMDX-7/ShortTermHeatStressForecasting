# 📁 Repository Structure

## Overview
The repository has been reorganized for better clarity and maintainability.

---

## 🏗️ Folder Organization

### Root Level
- **`app.py`** - Main Streamlit application (production)
- **`README.md`** - Main project documentation
- **`requirements.txt`** - Python dependencies

### 📊 `data/`
Weather and geographic data files:
- `weather.csv` - 1.1M hourly observations from 56 AQS stations (2018-2025)
- `metro.csv` - NYC metro county geographic information

### ⚙️ `config/`
Configuration and reference data:
- `sites.rds` - AQS monitoring site definitions
- `counties.rds` - County-level geographic data
- `csa.rds` - Combined Statistical Area data
- `bg.geojson` - Block group geographic boundaries

### 📚 `docs/`
User and developer documentation:
- `DASHBOARD_USER_GUIDE.md` - How to use the dashboard
- `TECHNICAL_ARCHITECTURE.md` - System design and implementation
- `QUICK_START.md` - Setup and deployment
- `PROJECT_COMPLETE.md` - Final deliverables
- `DOCUMENTATION_SUMMARY.md` - Documentation overview

### 📖 `documentation/`
Project deliverables and specifications:
- `00_START_HERE.md` - Project entry point
- `COMPLETION_SUMMARY.md` - Work completion summary
- `DASHBOARD_IMPLEMENTATION.md` - Dashboard specs
- `DASHBOARD_README.md` - Dashboard overview
- `README_DASHBOARD.md` - Additional dashboard docs
- `DELIVERABLES_CHECKLIST.md` - Project checklist
- `DOCUMENTATION_INDEX.md` - Documentation index

### 🔧 `misc/`
Miscellaneous and development files:
- `app_old.py` - Previous version (archived)
- `check_data.py` - Data validation script

### 🔒 `.git/`
Git repository metadata (not user-editable)

---

## 📋 File Purposes

### Core Application
| File | Purpose |
|------|---------|
| `app.py` | Production Streamlit dashboard |
| `requirements.txt` | Python package dependencies |

### Data
| File | Purpose | Size |
|------|---------|------|
| `weather.csv` | Hourly weather observations | ~1.1 million rows |
| `metro.csv` | County geographic reference | ~50 KB |

### Configuration
| File | Purpose |
|------|---------|
| `sites.rds` | AQS station metadata (56 sites) |
| `counties.rds` | County boundaries |
| `csa.rds` | Statistical areas |
| `bg.geojson` | Block group geometries |

### Documentation
| Location | Purpose |
|----------|---------|
| `docs/` | User & developer guides |
| `documentation/` | Project deliverables |

---

## 🚀 Quick Reference

### To Run the App
```bash
streamlit run app.py
```

### To Check Data
- Weather observations: `data/weather.csv`
- Metro configuration: `data/metro.csv`

### To Read Documentation
1. Start with: `documentation/00_START_HERE.md`
2. User guide: `docs/DASHBOARD_USER_GUIDE.md`
3. Technical: `docs/TECHNICAL_ARCHITECTURE.md`

---

## 📝 Adding New Files

- **New data files** → `data/`
- **New configuration** → `config/`
- **New documentation** → `docs/` (user-facing) or `documentation/` (internal)
- **Scripts/tools** → `misc/`

---

**Last Organized: December 5, 2025**
