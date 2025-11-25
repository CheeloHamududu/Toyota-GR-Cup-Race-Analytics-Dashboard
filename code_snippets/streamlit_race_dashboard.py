#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from race_analytics import RaceAnalytics

# Page config
st.set_page_config(
    page_title="Toyota GR Cup Race Dashboard",
    page_icon="🏁",
    layout="wide"
)

# Initialize analytics
@st.cache_resource
def load_analytics():
    return RaceAnalytics()

analytics = load_analytics()

# Main dashboard
st.title("🏁 Toyota GR Cup Real-Time Race Dashboard")

# Sidebar controls
st.sidebar.header("Race Controls")
vehicle_id = st.sidebar.selectbox("Vehicle", ["GR86-004-78", "GR86-005-12", "GR86-006-33"])
current_lap = st.sidebar.number_input("Current Lap", min_value=1, max_value=50, value=15)

# Real-time metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    position = st.number_input("Position", min_value=1, max_value=30, value=8)
    
with col2:
    fuel_pct = st.slider("Fuel %", 0, 100, 65)
    
with col3:
    tire_deg = st.slider("Tire Degradation %", 0, 100, 45)
    
with col4:
    gap_to_leader = st.number_input("Gap to Leader (s)", min_value=0.0, value=15.3)

# Main dashboard sections
col_left, col_right = st.columns([2, 1])

with col_left:
    # Pit strategy section
    st.subheader("🔧 Pit Strategy Analysis")
    
    pit_decision = analytics.pit_stop_window(vehicle_id, current_lap, fuel_pct, tire_deg)
    
    # Color-coded pit decision
    if pit_decision['action'] == 'PIT NOW':
        st.error(f"🚨 {pit_decision['action']}: {pit_decision['reason']}")
    elif pit_decision['action'] == 'PIT SOON':
        st.warning(f"⚠️ {pit_decision['action']}: {pit_decision['reason']}")
    else:
        st.success(f"✅ {pit_decision['action']}: {pit_decision['reason']}")
    
    # Fuel and tire gauges
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=("Fuel Level", "Tire Condition")
    )
    
    # Fuel gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=fuel_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Fuel %"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 20], 'color': "red"},
                {'range': [20, 40], 'color': "yellow"},
                {'range': [40, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 25
            }
        }
    ), row=1, col=1)
    
    # Tire degradation gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=tire_deg,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Tire Deg %"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [0, 50], 'color': "green"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    # Current status
    st.subheader("📊 Current Status")
    st.metric("Position", f"P{position}", delta=None)
    st.metric("Gap to Leader", f"+{gap_to_leader}s", delta=None)
    st.metric("Current Lap", current_lap, delta=None)
    
    # Quick calculations
    st.subheader("⚡ Quick Math")
    fuel_laps = fuel_pct / 5  # 5% per lap
    st.write(f"Fuel remaining: ~{fuel_laps:.1f} laps")
    
    tire_status = "CRITICAL" if tire_deg > 80 else "GOOD" if tire_deg < 50 else "MODERATE"
    st.write(f"Tire status: {tire_status}")

# Caution flag scenario
st.subheader("🟡 Caution Flag Strategy")
if st.button("CAUTION FLAG - Get Recommendations"):
    decisions = analytics.caution_response(vehicle_id, position, gap_to_leader, fuel_pct, tire_deg)
    
    for i, decision in enumerate(decisions, 1):
        if "PIT" in decision:
            st.warning(f"{i}. {decision}")
        else:
            st.info(f"{i}. {decision}")

# Lap time analysis
st.subheader("⏱️ Performance Analysis")
avg_lap = analytics.avg_lap_times.get(vehicle_id, 150)

# Simulate recent lap times
recent_laps = [avg_lap + np.random.normal(0, 2) for _ in range(10)]
lap_numbers = list(range(current_lap-9, current_lap+1))

fig_laps = go.Figure()
fig_laps.add_trace(go.Scatter(
    x=lap_numbers,
    y=recent_laps,
    mode='lines+markers',
    name='Lap Times',
    line=dict(color='blue', width=2)
))
fig_laps.add_hline(y=avg_lap, line_dash="dash", line_color="red", 
                   annotation_text=f"Average: {avg_lap:.1f}s")

fig_laps.update_layout(
    title="Recent Lap Times",
    xaxis_title="Lap Number",
    yaxis_title="Lap Time (seconds)",
    height=300
)
st.plotly_chart(fig_laps, use_container_width=True)

# Strategy recommendations
st.subheader("🎯 Strategic Recommendations")
qual_analysis = analytics.qualifying_impact()
st.info(f"📈 {qual_analysis['recommendation']}")
st.info("🔧 Focus on consistent pit stop execution")
st.info("🏎️ Monitor tire degradation closely in hot conditions")