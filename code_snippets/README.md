# Code Snippets - Toyota GR Cup Race Analytics

This folder contains Python scripts for analyzing Toyota GR Cup race data, providing real-time race strategy insights, and creating interactive dashboards.

## 📁 File Overview

### Core Analytics Engine
- **[race_analytics.py](race_analytics.py)** - Main analytics engine with comprehensive race strategy analysis
- **[race_analytics_simple.py](race_analytics_simple.py)** - Simplified version for quick race engineer decisions

### Machine Learning & Predictions
- **[race_predictive_model.py](race_predictive_model.py)** - Advanced ML models for race outcome predictions

### Data Processing
- **[create_bi_dataset.py](create_bi_dataset.py)** - Generates business intelligence datasets for external analysis

### Interactive Dashboards
- **[streamlit_race_app.py](streamlit_race_app.py)** - Full-featured web dashboard with BI dataset generation
- **[streamlit_race_dashboard.py](streamlit_race_dashboard.py)** - Real-time race monitoring dashboard

---

## 🔧 Detailed File Descriptions

### 1. race_analytics.py
**Purpose:** Core race analytics engine for strategic decision making

**Key Features:**
- Pit stop window optimization
- Caution flag strategy recommendations
- Real-time race dashboard
- Qualifying vs finish position correlation analysis
- Weather impact assessment

**Main Functions:**
- `pit_stop_window()` - Calculates optimal pit timing based on fuel/tire degradation
- `caution_response()` - Strategic decisions during caution periods
- `real_time_dashboard()` - Live race monitoring interface
- `qualifying_impact()` - Analyzes qualifying position importance

**Usage:**
```python
analytics = RaceAnalytics()
pit_decision = analytics.pit_stop_window('GR86-004-78', 15, 65, 45)
analytics.real_time_dashboard('GR86-004-78')
```

### 2. race_analytics_simple.py
**Purpose:** Lightweight race engineer tool for quick decisions

**Key Features:**
- Simplified pit strategy calculations
- Interactive race scenarios
- Caution flag decision matrix
- Real-time dashboard with minimal dependencies

**Main Functions:**
- `pit_stop_window()` - Basic pit timing calculations
- `caution_response()` - Quick caution decisions
- `real_time_dashboard()` - Simplified race monitoring
- `run_simulation()` - Interactive race scenarios

**Usage:**
```python
analytics = RaceAnalytics()
analytics.real_time_dashboard('GR86-004-78', current_lap=12, fuel_pct=55)
analytics.caution_scenario('GR86-004-78')
```

### 3. race_predictive_model.py
**Purpose:** Machine learning models for race predictions and strategy optimization

**Key Features:**
- Random Forest lap time prediction
- Race finish position forecasting
- Optimal pit window prediction
- Comprehensive strategy optimization
- Performance degradation modeling

**Main Functions:**
- `predict_lap_time()` - ML-based lap time prediction
- `predict_race_finish()` - Final position forecasting
- `predict_pit_window()` - Optimal pit timing with risk assessment
- `race_strategy_optimizer()` - Complete strategy recommendations

**Usage:**
```python
model = RacePredictiveModel()
strategy = model.race_strategy_optimizer('GR86-004-78', 15, 8, 65, 45)
lap_prediction = model.predict_lap_time('GR86-004-78', 16, 50, 60)
```

### 4. create_bi_dataset.py
**Purpose:** Generates clean, analysis-ready datasets for business intelligence tools

**Key Features:**
- Vehicle performance summaries
- Lap-by-lap analysis data
- Strategic insights compilation
- Race summary statistics
- Master BI dataset creation

**Generated Files:**
- `bi_vehicle_performance.csv` - Performance metrics per vehicle
- `bi_lap_analysis.csv` - Detailed lap-by-lap data
- `bi_strategic_insights.csv` - Key strategic findings
- `bi_race_summary.csv` - Overall race statistics
- `bi_master_dataset.csv` - Comprehensive combined dataset

**Usage:**
```python
from create_bi_dataset import create_bi_dataset
datasets = create_bi_dataset()
```

### 5. streamlit_race_app.py
**Purpose:** Full-featured web dashboard for comprehensive race analysis

**Key Features:**
- Interactive vehicle selection and comparison
- Real-time race parameter adjustment
- Live pit strategy recommendations
- Caution flag scenario simulation
- Integrated BI dataset generation
- Downloadable analysis reports

**Dashboard Sections:**
- Real-time analytics with customizable parameters
- Field overview with vehicle comparisons
- Interactive lap time charts
- Caution flag strategy simulator
- BI dataset generator with preview

**Usage:**
```bash
streamlit run streamlit_race_app.py
```

### 6. streamlit_race_dashboard.py
**Purpose:** Real-time race monitoring dashboard for race engineers

**Key Features:**
- Live race metrics display
- Fuel and tire condition gauges
- Pit strategy alerts
- Performance trend analysis
- Quick calculation tools

**Dashboard Components:**
- Real-time position and gap tracking
- Visual fuel/tire degradation gauges
- Lap time performance charts
- Strategic recommendation alerts

**Usage:**
```bash
streamlit run streamlit_race_dashboard.py
```

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install pandas numpy scikit-learn streamlit plotly warnings
```

### Required Data Files
Ensure these CSV files are in the same directory:
- `lap_times.csv`
- `telemetry_data_sampled.csv`
- `weather_data.csv`

### Quick Start Examples

**1. Basic Race Analysis:**
```python
from race_analytics import RaceAnalytics
analytics = RaceAnalytics()
analytics.real_time_dashboard('GR86-004-78')
```

**2. Predictive Strategy:**
```python
from race_predictive_model import RacePredictiveModel
model = RacePredictiveModel()
strategy = model.race_strategy_optimizer('GR86-004-78', 15, 8, 65, 45)
print(f"Recommendation: {strategy['recommendation']}")
```

**3. Interactive Dashboard:**
```bash
streamlit run streamlit_race_app.py
```

**4. Generate BI Datasets:**
```python
from create_bi_dataset import create_bi_dataset
datasets = create_bi_dataset()
```

---

## 📊 Use Cases

### Race Engineers
- **Real-time Strategy:** Use `race_analytics.py` for live race decisions
- **Quick Decisions:** Use `race_analytics_simple.py` for rapid pit calls
- **Visual Monitoring:** Use `streamlit_race_dashboard.py` for live tracking

### Data Analysts
- **Predictive Analysis:** Use `race_predictive_model.py` for forecasting
- **BI Integration:** Use `create_bi_dataset.py` for external tools
- **Interactive Analysis:** Use `streamlit_race_app.py` for exploration

### Team Management
- **Strategy Planning:** Combine all tools for comprehensive race preparation
- **Performance Review:** Use BI datasets for post-race analysis
- **Driver Development:** Analyze consistency and improvement trends

---

## 🔄 Workflow Integration

1. **Pre-Race:** Use predictive models to plan strategy
2. **During Race:** Monitor with real-time dashboards
3. **Pit Decisions:** Apply analytics engine recommendations
4. **Post-Race:** Generate BI datasets for analysis

## 📈 Key Metrics Tracked

- **Performance:** Lap times, consistency, pace analysis
- **Strategy:** Fuel consumption, tire degradation, pit timing
- **Position:** Track position, gaps, overtaking opportunities
- **Conditions:** Weather impact, track evolution

## 🎯 Strategic Insights

All tools emphasize:
- **Qualifying Priority:** Strong correlation between grid position and race result
- **Pit Stop Excellence:** Minimizing pit time for competitive advantage
- **Consistency Focus:** Reducing lap time variation improves overall performance
- **Data-Driven Decisions:** Using real-time metrics for strategic choices
