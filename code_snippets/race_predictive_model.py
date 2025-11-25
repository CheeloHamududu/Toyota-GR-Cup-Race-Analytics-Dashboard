#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class RacePredictiveModel:
    def __init__(self):
        self.lap_data = pd.read_csv('lap_times.csv')
        self.telemetry = pd.read_csv('telemetry_data_sampled.csv')
        self.weather = pd.read_csv('weather_data.csv')
        
        # Clean and prepare data
        self.lap_data['lap_time_sec'] = self.lap_data['value'] / 1000
        self.lap_data = self.lap_data[self.lap_data['value'] > 0]
        
        # Build models
        self.lap_time_model = None
        self.position_model = None
        self.fuel_model = None
        self._train_models()
    
    def _prepare_features(self):
        """Prepare features for machine learning"""
        # Lap time features
        lap_features = []
        for vehicle in self.lap_data['vehicle_id'].unique():
            vehicle_data = self.lap_data[self.lap_data['vehicle_id'] == vehicle].sort_values('lap')
            
            for i, row in vehicle_data.iterrows():
                if row['lap'] > 1:
                    prev_laps = vehicle_data[vehicle_data['lap'] < row['lap']]
                    if len(prev_laps) > 0:
                        features = {
                            'vehicle_id': vehicle,
                            'lap': row['lap'],
                            'current_lap_time': row['lap_time_sec'],
                            'avg_prev_laps': prev_laps['lap_time_sec'].mean(),
                            'tire_deg_est': (row['lap'] - 1) * 4,  # Estimated 4% per lap
                            'fuel_remaining': 100 - (row['lap'] - 1) * 5,  # 5% per lap
                            'track_position': np.random.randint(1, 32)  # Simulated position
                        }
                        lap_features.append(features)
        
        return pd.DataFrame(lap_features)
    
    def _train_models(self):
        """Train predictive models"""
        df = self._prepare_features()
        
        if len(df) > 10:
            # Lap time prediction model
            X_lap = df[['lap', 'avg_prev_laps', 'tire_deg_est', 'fuel_remaining']]
            y_lap = df['current_lap_time']
            
            self.lap_time_model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.lap_time_model.fit(X_lap, y_lap)
            
            # Position prediction model
            X_pos = df[['current_lap_time', 'avg_prev_laps', 'lap']]
            y_pos = df['track_position']
            
            self.position_model = LinearRegression()
            self.position_model.fit(X_pos, y_pos)
    
    def predict_lap_time(self, vehicle_id, current_lap, tire_deg, fuel_pct):
        """Predict next lap time"""
        if self.lap_time_model is None:
            return self._get_baseline_lap_time(vehicle_id)
        
        # Get historical average
        vehicle_data = self.lap_data[self.lap_data['vehicle_id'] == vehicle_id]
        avg_prev = vehicle_data['lap_time_sec'].mean() if len(vehicle_data) > 0 else 150
        
        # Predict
        features = np.array([[current_lap, avg_prev, tire_deg, fuel_pct]])
        predicted_time = self.lap_time_model.predict(features)[0]
        
        return max(predicted_time, avg_prev * 0.95)  # Minimum bound
    
    def predict_race_finish(self, vehicle_id, current_lap, current_pos, fuel_pct, tire_deg):
        """Predict final race position"""
        # Calculate remaining performance
        remaining_laps = 20 - current_lap
        predicted_lap_time = self.predict_lap_time(vehicle_id, current_lap, tire_deg, fuel_pct)
        
        # Performance degradation
        tire_impact = (tire_deg / 100) * 2  # Up to 2s penalty
        fuel_impact = max(0, (40 - fuel_pct) / 40) * 1  # Up to 1s penalty if low fuel
        
        adjusted_lap_time = predicted_lap_time + tire_impact + fuel_impact
        
        # Simple position prediction based on pace
        all_vehicles = self.lap_data['vehicle_id'].unique()
        avg_times = self.lap_data.groupby('vehicle_id')['lap_time_sec'].mean()
        
        # Rank by predicted performance
        vehicle_performance = avg_times.get(vehicle_id, 150) + tire_impact + fuel_impact
        better_vehicles = sum(1 for v in all_vehicles if avg_times.get(v, 150) < vehicle_performance)
        
        predicted_position = max(1, min(better_vehicles + 1, len(all_vehicles)))
        
        return {
            'predicted_position': predicted_position,
            'predicted_lap_time': adjusted_lap_time,
            'tire_impact': tire_impact,
            'fuel_impact': fuel_impact,
            'confidence': 0.85 if remaining_laps < 10 else 0.70
        }
    
    def predict_pit_window(self, vehicle_id, current_lap, fuel_pct, tire_deg, target_laps):
        """Predict optimal pit window"""
        pit_scenarios = []
        
        for pit_lap in range(current_lap + 1, current_lap + 6):
            if pit_lap > target_laps:
                break
                
            # Calculate stint performance
            laps_to_pit = pit_lap - current_lap
            fuel_at_pit = fuel_pct - (laps_to_pit * 5)
            tire_at_pit = tire_deg + (laps_to_pit * 4)
            
            if fuel_at_pit < 5:  # Can't make it
                continue
            
            # Performance degradation before pit
            avg_degradation = (tire_at_pit / 100) * 1.5
            
            # Time lost in pit (30s) vs time gained with fresh tires
            pit_time_loss = 30
            remaining_laps = target_laps - pit_lap
            tire_time_gain = remaining_laps * avg_degradation
            
            net_benefit = tire_time_gain - pit_time_loss
            
            pit_scenarios.append({
                'pit_lap': pit_lap,
                'fuel_at_pit': fuel_at_pit,
                'tire_at_pit': tire_at_pit,
                'net_benefit': net_benefit,
                'risk_level': 'LOW' if fuel_at_pit > 20 else 'MEDIUM' if fuel_at_pit > 10 else 'HIGH'
            })
        
        if pit_scenarios:
            best_scenario = max(pit_scenarios, key=lambda x: x['net_benefit'])
            return best_scenario
        
        return {'pit_lap': current_lap + 1, 'net_benefit': 0, 'risk_level': 'CRITICAL'}
    
    def _get_baseline_lap_time(self, vehicle_id):
        """Get baseline lap time for vehicle"""
        vehicle_data = self.lap_data[self.lap_data['vehicle_id'] == vehicle_id]
        return vehicle_data['lap_time_sec'].mean() if len(vehicle_data) > 0 else 150.0
    
    def race_strategy_optimizer(self, vehicle_id, current_lap, current_pos, fuel_pct, tire_deg):
        """Comprehensive race strategy optimization"""
        race_prediction = self.predict_race_finish(vehicle_id, current_lap, current_pos, fuel_pct, tire_deg)
        pit_prediction = self.predict_pit_window(vehicle_id, current_lap, fuel_pct, tire_deg, 20)
        
        # Strategy recommendations
        strategy = {
            'predicted_finish': race_prediction['predicted_position'],
            'confidence': race_prediction['confidence'],
            'optimal_pit_lap': pit_prediction['pit_lap'],
            'pit_benefit': pit_prediction['net_benefit'],
            'risk_assessment': pit_prediction['risk_level']
        }
        
        # Generate recommendations
        if pit_prediction['net_benefit'] > 5:
            strategy['recommendation'] = f"PIT on lap {pit_prediction['pit_lap']} for {pit_prediction['net_benefit']:.1f}s gain"
        elif fuel_pct < 25:
            strategy['recommendation'] = "PIT SOON - Fuel critical"
        elif tire_deg > 85:
            strategy['recommendation'] = "PIT SOON - Tire degradation critical"
        else:
            strategy['recommendation'] = "STAY OUT - Current strategy optimal"
        
        return strategy

# Demo usage
if __name__ == "__main__":
    model = RacePredictiveModel()
    
    # Test predictions
    vehicle = 'GR86-004-78'
    strategy = model.race_strategy_optimizer(vehicle, 15, 8, 65, 45)
    
    print(f"🔮 PREDICTIVE RACE STRATEGY - {vehicle}")
    print("=" * 50)
    print(f"Predicted Finish: P{strategy['predicted_finish']} (Confidence: {strategy['confidence']:.0%})")
    print(f"Optimal Pit Lap: {strategy['optimal_pit_lap']}")
    print(f"Strategy: {strategy['recommendation']}")