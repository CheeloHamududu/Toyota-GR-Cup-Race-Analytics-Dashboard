#!/usr/bin/env python3
import csv
import json
from datetime import datetime

class RaceAnalytics:
    def __init__(self):
        # Load lap times data
        self.lap_data = []
        with open('lap_times.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['value'] and row['value'] != '0':
                    self.lap_data.append({
                        'vehicle_id': row['vehicle_id'],
                        'lap': int(row['lap']),
                        'time_ms': int(row['value']),
                        'time_sec': int(row['value']) / 1000
                    })
        
        # Calculate average lap times
        self.avg_times = {}
        for vehicle in set(row['vehicle_id'] for row in self.lap_data):
            times = [row['time_sec'] for row in self.lap_data if row['vehicle_id'] == vehicle]
            self.avg_times[vehicle] = sum(times) / len(times) if times else 150
    
    def pit_stop_window(self, vehicle_id, current_lap, fuel_pct, tire_deg_pct):
        """Calculate optimal pit stop window"""
        avg_lap = self.avg_times.get(vehicle_id, 150)
        pit_penalty = 30  # seconds
        
        # Fuel analysis
        fuel_laps_remaining = fuel_pct / 5  # 5% per lap
        
        # Tire degradation impact
        tire_penalty = (tire_deg_pct / 10) * 0.5
        
        if fuel_laps_remaining < 3:
            return {"action": "🚨 PIT NOW", "reason": "CRITICAL FUEL", "urgency": "HIGH"}
        elif tire_deg_pct > 80:
            return {"action": "🔧 PIT SOON", "reason": "High tire wear", "time_loss": f"{tire_penalty:.1f}s/lap"}
        elif fuel_laps_remaining < 5 and tire_deg_pct > 60:
            return {"action": "📋 PIT WINDOW", "reason": "Fuel + tire strategy", "window": f"Laps {current_lap+1}-{current_lap+3}"}
        else:
            return {"action": "✅ STAY OUT", "reason": "Good window", "next_check": current_lap + 3}
    
    def caution_response(self, position, gap_to_leader, fuel_pct, tire_deg):
        """Caution flag strategy"""
        decisions = []
        
        if fuel_pct < 40 or tire_deg > 70:
            decisions.append("🔧 PIT - Free stop opportunity")
        elif position > 10 and gap_to_leader > 30:
            decisions.append("📈 PIT - Gain track position")
        else:
            decisions.append("🏁 STAY OUT - Protect position")
            
        if position <= 3:
            decisions.append("🥇 PRIORITY: Defend podium position")
        elif fuel_pct > 60 and tire_deg < 50:
            decisions.append("🎯 OPPORTUNITY: Stay out for position gain")
            
        return decisions
    
    def real_time_dashboard(self, vehicle_id, current_lap=10, fuel_pct=65, tire_deg=45, position=8, gap_to_leader=15.3):
        """Main race engineer dashboard"""
        print(f"\n🏁 TOYOTA GR CUP - RACE ANALYTICS")
        print(f"Vehicle: {vehicle_id}")
        print("=" * 60)
        
        # Current status
        print(f"📍 POSITION: P{position} (+{gap_to_leader}s to leader)")
        print(f"⛽ FUEL: {fuel_pct}% | 🏎️ TIRE WEAR: {tire_deg}%")
        print(f"🔄 LAP: {current_lap}/20")
        
        # Pit strategy
        pit_decision = self.pit_stop_window(vehicle_id, current_lap, fuel_pct, tire_deg)
        print(f"\n🔧 PIT STRATEGY")
        print(f"   Decision: {pit_decision['action']}")
        print(f"   Reason: {pit_decision['reason']}")
        
        # Performance metrics
        avg_lap = self.avg_times.get(vehicle_id, 150)
        print(f"\n⏱️ PERFORMANCE")
        print(f"   Average lap: {avg_lap:.1f}s")
        print(f"   Pace vs field: {'STRONG' if avg_lap < 152 else 'COMPETITIVE' if avg_lap < 155 else 'NEEDS WORK'}")
        
        # Strategic recommendations
        print(f"\n🎯 RECOMMENDATIONS")
        print("   • Qualifying Focus: Starting position = race result")
        print("   • Pit Training: Every 0.1s saved = track position")
        print("   • Driver Development: Experience accelerates pace")
        
        return pit_decision
    
    def caution_scenario(self, vehicle_id, position=8, gap=15.3, fuel=65, tire_deg=45):
        """Caution flag decision matrix"""
        print(f"\n🟡 CAUTION FLAG DEPLOYED")
        print("⚠️ IMMEDIATE DECISION REQUIRED")
        print("=" * 40)
        
        decisions = self.caution_response(position, gap, fuel, tire_deg)
        
        print("📋 STRATEGY OPTIONS:")
        for i, decision in enumerate(decisions, 1):
            print(f"   {i}. {decision}")
        
        # Quick calculations
        fuel_laps = fuel / 5
        print(f"\n📊 SITUATION ANALYSIS:")
        print(f"   Fuel remaining: ~{fuel_laps:.1f} laps")
        print(f"   Tire status: {'🔴 CRITICAL' if tire_deg > 80 else '🟡 MODERATE' if tire_deg > 50 else '🟢 GOOD'}")
        print(f"   Track position: {'🥇 PODIUM FIGHT' if position <= 3 else '🏆 POINTS BATTLE' if position <= 10 else '📈 RECOVERY MODE'}")
        
        return decisions

# Interactive simulation
def run_simulation():
    analytics = RaceAnalytics()
    
    print("🏁 TOYOTA GR CUP RACE ENGINEER SIMULATOR")
    print("Real-time decision making tool")
    
    # Scenario 1: Mid-race situation
    print("\n" + "="*60)
    print("SCENARIO 1: MID-RACE STRATEGY")
    analytics.real_time_dashboard('GR86-004-78', current_lap=12, fuel_pct=55, tire_deg=65, position=6, gap_to_leader=8.2)
    
    # Scenario 2: Caution flag
    print("\n" + "="*60)
    print("SCENARIO 2: CAUTION FLAG RESPONSE")
    analytics.caution_scenario('GR86-004-78', position=6, gap=8.2, fuel=55, tire_deg=65)
    
    # Scenario 3: Critical fuel
    print("\n" + "="*60)
    print("SCENARIO 3: FUEL CRITICAL")
    analytics.real_time_dashboard('GR86-010-16', current_lap=18, fuel_pct=12, tire_deg=85, position=4, gap_to_leader=3.1)

if __name__ == "__main__":
    run_simulation()