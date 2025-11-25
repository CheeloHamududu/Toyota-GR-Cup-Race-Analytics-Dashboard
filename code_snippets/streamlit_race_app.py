#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from race_analytics import RaceAnalytics
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="Toyota GR Cup Race Analytics", layout="wide")

@st.cache_data
def load_analytics():
    return RaceAnalytics()

def main():
    st.title("🏁 Toyota GR Cup Race Analytics Dashboard")
    
    # Load analytics
    analytics = load_analytics()
    
    # Sidebar for car selection
    st.sidebar.header("🏎️ Vehicle Selection")
    available_cars = list(analytics.avg_lap_times.index)
    selected_car = st.sidebar.selectbox("Select Vehicle", available_cars, key="vehicle_selector")
    
    # Current race parameters
    st.sidebar.header("📊 Current Race Status")
    current_lap = st.sidebar.slider("Current Lap", 1, 50, 15, key=f"lap_{selected_car}")
    fuel_pct = st.sidebar.slider("Fuel %", 0, 100, 65, key=f"fuel_{selected_car}")
    tire_deg = st.sidebar.slider("Tire Degradation %", 0, 100, 45, key=f"tire_{selected_car}")
    position = st.sidebar.slider("Current Position", 1, len(available_cars), 8, key=f"pos_{selected_car}")
    gap_to_leader = st.sidebar.number_input("Gap to Leader (seconds)", 0.0, 120.0, 15.3, key=f"gap_{selected_car}")
    
    # Main dashboard
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"🎯 Real-Time Analytics: {selected_car}")
        st.caption(f"Average lap time: {analytics.avg_lap_times[selected_car]:.2f}s")
        
        # Get pit decision
        pit_decision = analytics.pit_stop_window(selected_car, current_lap, fuel_pct, tire_deg)
        
        # Status cards
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            st.metric("Position", f"#{position}", f"Gap: +{gap_to_leader}s")
        
        with status_col2:
            st.metric("Fuel Level", f"{fuel_pct}%", f"~{fuel_pct/5:.1f} laps")
        
        with status_col3:
            tire_status = "🔴 Critical" if tire_deg > 80 else "🟡 Moderate" if tire_deg > 50 else "🟢 Good"
            st.metric("Tire Condition", f"{tire_deg}%", tire_status)
        
        # Pit strategy alert
        action_color = {"PIT NOW": "🔴", "PIT SOON": "🟡", "PIT NEXT 2 LAPS": "🟡", "STAY OUT": "🟢"}
        st.info(f"{action_color.get(pit_decision['action'], '🔵')} **{pit_decision['action']}** - {pit_decision['reason']}")
        
        # Lap times chart
        st.subheader("⏱️ Lap Time Performance")
        lap_data_filtered = analytics.lap_data[analytics.lap_data['vehicle_id'] == selected_car].copy()
        
        if not lap_data_filtered.empty:
            # Filter out invalid lap times (0 values and outliers)
            lap_data_filtered = lap_data_filtered[lap_data_filtered['value'] > 0]
            lap_data_filtered = lap_data_filtered[lap_data_filtered['lap'] <= 25]  # Reasonable lap limit
            
            if not lap_data_filtered.empty:
                fig = px.line(lap_data_filtered, x='lap', y='lap_time_sec', 
                             title=f"Lap Times - {selected_car}")
                fig.add_hline(y=analytics.avg_lap_times[selected_car], 
                             line_dash="dash", annotation_text="Average")
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{selected_car}")
            else:
                st.info(f"No valid lap data available for {selected_car}")
        else:
            st.info(f"No lap data available for {selected_car}")
        
    with col2:
        st.header("🏆 Field Overview")
        
        # Vehicle selector for comparison
        compare_car = st.selectbox("Compare with:", available_cars, 
                                  index=available_cars.index(selected_car), 
                                  key="compare_selector")
        
        if compare_car != selected_car:
            time_diff = analytics.avg_lap_times[selected_car] - analytics.avg_lap_times[compare_car]
            if time_diff > 0:
                st.info(f"📊 {selected_car} is {time_diff:.2f}s slower than {compare_car}")
            else:
                st.success(f"📊 {selected_car} is {abs(time_diff):.2f}s faster than {compare_car}")
        
        # Interactive average lap times
        st.subheader("⏱️ Average Lap Times")
        
        performance_df = pd.DataFrame({
            'Vehicle': analytics.avg_lap_times.index,
            'Avg Lap Time': analytics.avg_lap_times.values
        }).sort_values('Avg Lap Time')
        
        # Interactive chart with hover and click
        performance_df['Selected'] = performance_df['Vehicle'] == selected_car
        performance_df['Color'] = performance_df['Selected'].map({True: 'Selected', False: 'Other'})
        
        fig_bar = px.bar(performance_df, 
                        x='Avg Lap Time', 
                        y='Vehicle',
                        color='Color',
                        orientation='h',
                        title="Click on any car to compare",
                        hover_data={'Avg Lap Time': ':.2f'},
                        color_discrete_map={'Selected': '#ff6b6b', 'Other': '#4ecdc4'})
        
        fig_bar.update_layout(showlegend=False, height=400)
        fig_bar.update_traces(hovertemplate='<b>%{y}</b><br>Avg Lap Time: %{x:.2f}s<extra></extra>')
        
        st.plotly_chart(fig_bar, use_container_width=True, key="field_overview")
        
        # Interactive data table
        st.write("**Lap Time Comparison:**")
        comparison_df = performance_df[['Vehicle', 'Avg Lap Time']].copy()
        comparison_df['Gap to Fastest'] = comparison_df['Avg Lap Time'] - comparison_df['Avg Lap Time'].min()
        comparison_df['Gap to Selected'] = abs(comparison_df['Avg Lap Time'] - analytics.avg_lap_times[selected_car])
        
        st.dataframe(
            comparison_df.style.format({
                'Avg Lap Time': '{:.2f}s',
                'Gap to Fastest': '+{:.2f}s',
                'Gap to Selected': '{:.2f}s'
            }).highlight_max(subset=['Gap to Fastest'], color='lightcoral')
             .highlight_min(subset=['Avg Lap Time'], color='lightgreen'),
            use_container_width=True
        )
        
        # Weather conditions
        st.subheader("🌤️ Weather Status")
        current_weather = analytics.weather.iloc[-1]
        if current_weather['RAIN'] > 0:
            st.warning("🌧️ Rain detected - Consider tire strategy")
        else:
            st.info("☀️ Dry conditions")
        
        # Performance metrics
        st.subheader("📈 Performance Metrics")
        fastest_time = performance_df['Avg Lap Time'].min()
        selected_time = analytics.avg_lap_times[selected_car]
        gap_to_fastest = selected_time - fastest_time
        
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Fastest Car", performance_df.iloc[0]['Vehicle'], f"{fastest_time:.2f}s")
        with metric_col2:
            st.metric("Gap to Fastest", f"+{gap_to_fastest:.2f}s", 
                     "🟢 Competitive" if gap_to_fastest < 1.0 else "🟡 Moderate" if gap_to_fastest < 2.0 else "🔴 Significant")
        
    # Caution flag scenario
    st.header("🟡 Caution Flag Strategy")
    if st.button("Simulate Caution Flag", key=f"caution_{selected_car}"):
        st.subheader(f"⚠️ CAUTION - Lap {current_lap}")
        
        # Real-time caution analysis
        fuel_laps = fuel_pct / 5
        pit_window = "CRITICAL" if fuel_laps < 3 else "OPTIMAL" if fuel_laps < 8 else "GOOD"
        tire_condition = "CRITICAL" if tire_deg > 80 else "WORN" if tire_deg > 60 else "GOOD"
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Current Status:**")
            st.write(f"• Position: P{position} (+{gap_to_leader}s)")
            st.write(f"• Fuel: {fuel_pct}% ({fuel_laps:.1f} laps)")
            st.write(f"• Tires: {tire_deg}% wear")
        
        with col2:
            st.write("**Caution Decision:**")
            if fuel_pct < 40 or tire_deg > 70:
                st.error("🔴 **PIT NOW** - Critical window")
                st.write("Reason: Low fuel/worn tires")
            elif position > 10:
                st.warning("🟡 **PIT** - Gain positions")
                st.write("Reason: Free track position")
            else:
                st.success("🟢 **STAY OUT** - Hold position")
                st.write("Reason: Protect current standing")
    
    # Strategy insights
    st.header("🎯 Strategic Insights")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Qualifying Correlation", "0.99")
        st.write("HIGH PRIORITY: Qualifying performance")
    
    with col2:
        st.write(f"**Race Strategy for {selected_car}:**")
        if position <= 5:
            st.write("• Conservative approach - protect position")
        else:
            st.write("• Aggressive strategy - gain positions")
        st.write("• Monitor tire degradation closely")
        st.write("• Fuel management critical for stint length")

    # BI Dataset Generator
    st.header("📊 BI Dataset Generator")
    if st.button("Generate BI Datasets", type="primary"):
        with st.spinner("Creating BI-ready datasets..."):
            from create_bi_dataset import create_bi_dataset
            datasets = create_bi_dataset()
            
            st.success("✅ BI Datasets Created Successfully!")
            
            # Show dataset previews
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Master Dataset", "Vehicle Performance", "Lap Analysis", "Strategic Insights", "Race Summary"])
            
            with tab1:
                st.subheader("Master BI Dataset")
                st.dataframe(datasets['master_dataset'], use_container_width=True)
                st.download_button("Download Master Dataset", 
                                 datasets['master_dataset'].to_csv(index=False),
                                 "bi_master_dataset.csv", "text/csv")
            
            with tab2:
                st.subheader("Vehicle Performance Analysis")
                st.dataframe(datasets['vehicle_performance'], use_container_width=True)
                st.download_button("Download Performance Data", 
                                 datasets['vehicle_performance'].to_csv(index=False),
                                 "bi_vehicle_performance.csv", "text/csv")
            
            with tab3:
                st.subheader("Lap-by-Lap Analysis")
                st.dataframe(datasets['lap_analysis'].head(20), use_container_width=True)
                st.write(f"Total records: {len(datasets['lap_analysis'])}")
                st.download_button("Download Lap Analysis", 
                                 datasets['lap_analysis'].to_csv(index=False),
                                 "bi_lap_analysis.csv", "text/csv")
            
            with tab4:
                st.subheader("Strategic Insights")
                st.dataframe(datasets['strategic_insights'], use_container_width=True)
                st.download_button("Download Strategic Insights", 
                                 datasets['strategic_insights'].to_csv(index=False),
                                 "bi_strategic_insights.csv", "text/csv")
            
            with tab5:
                st.subheader("Race Summary Statistics")
                st.dataframe(datasets['race_summary'], use_container_width=True)
                st.download_button("Download Race Summary", 
                                 datasets['race_summary'].to_csv(index=False),
                                 "bi_race_summary.csv", "text/csv")

if __name__ == "__main__":
    main()