#!/usr/bin/env python3
"""
Continuous data generator that keeps generating data without getting stuck.
"""

import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta
import os
from ews_model import (
    EWSConfig, compute_cai, compute_cdi, normalize_thi, thi_celsius,
    normalize_ti, normalize_ei, compute_behavioral_intention,
    AlertEngine
)

class ContinuousDataGenerator:
    def __init__(self, csv_file='ews_demo.csv'):
        self.csv_file = csv_file
        self.config = EWSConfig()
        self.alert_engine = AlertEngine(self.config)
        self.current_time = datetime.now()
        self.scenario_phase = "normal"
        self.scenario_intensity = 0.0
        self.data_counter = 0
        # Demo mode: force alert occurrence probabilities using Risk only
        # Target mix: green 40%, yellow 30%, orange 20%, red 10%
        self.force_alert_probs = True
        
        # Load existing data or create new
        if os.path.exists(csv_file):
            self.df = pd.read_csv(csv_file, parse_dates=['timestamp'])
            self.current_time = self.df['timestamp'].iloc[-1] + timedelta(minutes=5)
        else:
            self.df = pd.DataFrame()
    
    def generate_scenario(self):
        """Generate realistic scenarios for different crowd situations"""
        hour = self.current_time.hour
        day_of_week = self.current_time.weekday()
        
        # Simulate different scenarios with more randomness and higher risk scenarios
        scenarios = [
            {"name": "normal", "probability": 0.3, "intensity": 0.1},
            {"name": "morning_rush", "probability": 0.25, "intensity": 0.4},
            {"name": "evening_rush", "probability": 0.25, "intensity": 0.5},
            {"name": "festival_peak", "probability": 0.15, "intensity": 0.8},
            {"name": "emergency_situation", "probability": 0.05, "intensity": 0.9}
        ]
        
        # Choose scenario based on time and probability with EXTREME randomness
        rand = random.random()
        if 6 <= hour <= 10 and rand < 0.45:  # Morning rush (slightly less frequent)
            scenario = scenarios[1]
        elif 17 <= hour <= 21 and rand < 0.45:  # Evening rush
            scenario = scenarios[2]
        elif rand < 0.05:  # Emergency rarer
            scenario = scenarios[4]
        elif rand < 0.12:  # Festival peak less frequent
            scenario = scenarios[3]
        else:
            scenario = scenarios[0]
        
        self.scenario_phase = scenario["name"]
        self.scenario_intensity = scenario["intensity"]
        
        return scenario
    
    def generate_crowd_data(self):
        """Generate realistic crowd data based on current scenario"""
        scenario = self.generate_scenario()
        
        # Add EXTREME dynamic variation with very high amplitude
        self.data_counter += 1
        cycle_factor = np.sin(2 * np.pi * self.data_counter / 10) * 1.2
        random_factor = random.gauss(0, 1.5)
        
        # Add occasional extreme spikes
        if random.random() < 0.1:  # 10% chance of extreme spike
            random_factor += random.choice([-2, 2]) * random.random()
        
        # Environmental conditions with moderated variation (to allow more green)
        base_temp = 20 + 10 * np.sin(2 * np.pi * self.current_time.hour / 24)
        temp_c = base_temp + random.gauss(0, 6) + scenario["intensity"] * 10 + cycle_factor * 4
        temp_c = max(5, min(50, temp_c))
        
        rh = 70 - (temp_c - 20) * 2 + random.gauss(0, 10) + cycle_factor * 4
        rh = max(15, min(95, rh))
        
        thi_raw = thi_celsius(temp_c, rh)
        thi = normalize_thi(thi_raw)
        
        # Crowd dynamics based on scenario with MUCH enhanced fluctuation
        if scenario["name"] == "emergency_situation":
            base_density = 4.5 + cycle_factor * 1.0 + random_factor * 0.8
            density = base_density + random.gauss(0, 1.2)
            speed = 0.05 + random.gauss(0, 0.2) + cycle_factor * 0.1
            speed_var = 0.25 + random.gauss(0, 0.15) + abs(cycle_factor) * 0.1
            push_rate = 15 + random.gauss(0, 8) + abs(cycle_factor) * 6
            shout_rate = 25 + random.gauss(0, 10) + abs(cycle_factor) * 8
            near_falls = 10 + random.gauss(0, 5) + abs(cycle_factor) * 4
            
            ati = 0.95 + random.gauss(0, 0.1) + cycle_factor * 0.08
            sni = 0.98 + random.gauss(0, 0.08) + cycle_factor * 0.05
            pci = 0.02 + random.gauss(0, 0.08) - abs(cycle_factor) * 0.05
            
        elif scenario["name"] == "festival_peak":
            base_density = 4.0 + cycle_factor * 0.8 + random_factor * 0.6
            density = base_density + random.gauss(0, 1.0)
            speed = 0.2 + random.gauss(0, 0.25) + cycle_factor * 0.15
            speed_var = 0.2 + random.gauss(0, 0.1) + abs(cycle_factor) * 0.08
            push_rate = 12 + random.gauss(0, 6) + abs(cycle_factor) * 4
            shout_rate = 20 + random.gauss(0, 8) + abs(cycle_factor) * 6
            near_falls = 8 + random.gauss(0, 4) + abs(cycle_factor) * 3
            
            ati = 0.85 + random.gauss(0, 0.15) + cycle_factor * 0.1
            sni = 0.9 + random.gauss(0, 0.12) + cycle_factor * 0.08
            pci = 0.15 + random.gauss(0, 0.12) - abs(cycle_factor) * 0.08
            
        elif scenario["name"] in ["morning_rush", "evening_rush"]:
            base_density = 3.0 + cycle_factor * 0.6 + random_factor * 0.4
            density = base_density + random.gauss(0, 0.8)
            speed = 0.4 + random.gauss(0, 0.3) + cycle_factor * 0.2
            speed_var = 0.15 + random.gauss(0, 0.08) + abs(cycle_factor) * 0.06
            push_rate = 6 + random.gauss(0, 4) + abs(cycle_factor) * 3
            shout_rate = 12 + random.gauss(0, 6) + abs(cycle_factor) * 4
            near_falls = 4 + random.gauss(0, 3) + abs(cycle_factor) * 2
            
            ati = 0.7 + random.gauss(0, 0.2) + cycle_factor * 0.12
            sni = 0.8 + random.gauss(0, 0.15) + cycle_factor * 0.1
            pci = 0.3 + random.gauss(0, 0.15) - abs(cycle_factor) * 0.08
            
        else:  # normal
            base_density = 1.5 + cycle_factor * 0.4 + random_factor * 0.3
            density = base_density + random.gauss(0, 0.6)
            speed = 0.8 + random.gauss(0, 0.25) + cycle_factor * 0.2
            speed_var = 0.08 + random.gauss(0, 0.04) + abs(cycle_factor) * 0.03
            push_rate = 1.5 + random.gauss(0, 1.2) + abs(cycle_factor) * 0.8
            shout_rate = 4 + random.gauss(0, 3) + abs(cycle_factor) * 2
            near_falls = 0.8 + random.gauss(0, 0.6) + abs(cycle_factor) * 0.4
            
            ati = 0.4 + random.gauss(0, 0.18) + cycle_factor * 0.12
            sni = 0.5 + random.gauss(0, 0.18) + cycle_factor * 0.1
            pci = 0.5 + random.gauss(0, 0.18) - abs(cycle_factor) * 0.08
        
        # Clamp values to realistic ranges
        density = max(0.1, min(5.0, density))
        speed = max(0.05, min(1.5, speed))
        speed_var = max(0.01, min(0.3, speed_var))
        push_rate = max(0, min(25, push_rate))
        shout_rate = max(0, min(30, shout_rate))
        near_falls = max(0, min(15, near_falls))
        ati = max(0, min(1, ati))
        sni = max(0, min(1, sni))
        pci = max(0, min(1, pci))
        
        # Compute indices
        cai = compute_cai(push_rate, shout_rate, near_falls, density)
        cdi = compute_cdi(density, speed, speed_var)
        ti = normalize_ti(self.current_time.hour)
        ei = normalize_ei(scenario["name"])
        
        # Compute behavioral intention
        bi = compute_behavioral_intention(ati, sni, pci)
        
        # Compute risks
        physical_risk = (self.config.weights["CAI"]*cai + 
                        self.config.weights["CDI"]*cdi +
                        self.config.weights["THI"]*thi + 
                        self.config.weights["TI"]*ti + 
                        self.config.weights["EI"]*ei)
        
        # Determine alert level
        if self.force_alert_probs:
            th = self.config.thresholds
            r = random.random()
            if r < 0.40:
                alert = 'green'; lo, hi = 0.08, max(0.0, th['yellow'] - 0.02)
            elif r < 0.70:
                alert = 'yellow'; lo, hi = th['yellow'] + 0.01, th['orange'] - 0.02
            elif r < 0.90:
                alert = 'orange'; lo, hi = th['orange'] + 0.01, th['red'] - 0.02
            else:
                alert = 'red'; lo, hi = th['red'] + 0.03, min(0.98, th['red'] + 0.2)
            # Fallback to midpoints if ranges collapse
            if hi <= lo:
                mid = {
                    'green': 0.2,
                    'yellow': (th['yellow'] + th['orange'])/2.0,
                    'orange': (th['orange'] + th['red'])/2.0,
                    'red': min(0.95, th['red'] + 0.1)
                }
                physical_risk = mid[alert]
            else:
                physical_risk = max(0.0, min(1.0, random.uniform(lo, hi)))
        else:
            # Use configured thresholds with hysteresis on Risk
            alert = self.alert_engine.step(physical_risk)
        
        return {
            'timestamp': self.current_time,
            'phase': scenario["name"],
            'temp_c': round(temp_c, 2),
            'rh': round(rh, 1),
            'THI_raw': round(thi_raw, 2),
            'THI': round(thi, 3),
            'density_p_m2': round(density, 2),
            'speed_mps': round(speed, 2),
            'speed_var': round(speed_var, 3),
            'push_rate': round(push_rate, 2),
            'shout_rate': round(shout_rate, 2),
            'near_falls': round(near_falls, 2),
            'CAI': round(cai, 3),
            'CDI': round(cdi, 3),
            'TI': round(ti, 3),
            'EI': round(ei, 3),
            'ATI': round(ati, 3),
            'SNI': round(sni, 3),
            'PCI': round(pci, 3),
            'BI': round(bi, 3),
            'Risk': round(physical_risk, 3),
            'Alert': alert
        }
    
    def update_csv(self, new_data):
        """Add new data point to CSV file"""
        new_row = pd.DataFrame([new_data])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        
        # Keep only last 1000 data points to prevent file from growing too large
        if len(self.df) > 1000:
            self.df = self.df.tail(1000)
        
        # Save to CSV with Risk-only columns
        desired_cols = [
            'timestamp','phase','temp_c','rh','THI_raw','THI',
            'density_p_m2','speed_mps','speed_var','push_rate','shout_rate','near_falls',
            'CAI','CDI','TI','EI','ATI','SNI','PCI','BI','Risk','Alert'
        ]
        present = [c for c in desired_cols if c in self.df.columns]
        # Reassign to drop any extra columns like RiskExtended from older files
        self.df = self.df[present].copy()
        self.df.to_csv(self.csv_file, index=False)
    
    def run_continuous(self, interval_seconds=3):
        """Run continuous data generation"""
        print(f"🚀 Starting Continuous TPB-Enhanced EWS Data Generation")
        print(f"⏱️  Update interval: {interval_seconds} seconds")
        print(f"📁 Data file: {self.csv_file}")
        print("-" * 60)
        
        try:
            while True:
                # Generate new data point
                new_data = self.generate_crowd_data()
                
                # Update CSV
                self.update_csv(new_data)
                
                # Print status
                timestamp_str = new_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"⏰ {timestamp_str} | "
                      f"Phase: {new_data['phase']:12} | "
                      f"Risk: {new_data['Risk']:.3f} | "
                      f"Alert: {new_data['Alert']:5} | "
                      f"Density: {new_data['density_p_m2']:.1f}")
                
                # Wait for next update
                time.sleep(interval_seconds)
                
                # Advance time by the interval specified
                self.current_time += timedelta(seconds=interval_seconds)
        
        except KeyboardInterrupt:
            print("\n🛑 Continuous generation stopped by user")

def main():
    generator = ContinuousDataGenerator()
    
    print("TPB-Enhanced EWS Continuous Data Generator")
    print("=" * 50)
    print("This script generates realistic crowd data continuously")
    print("and updates the CSV file for live dashboard visualization.")
    print()
    
    try:
        interval = int(input("Enter update interval in seconds (default 3): ") or "3")
        generator.run_continuous(interval)
        
    except ValueError:
        print("Invalid input. Using default values.")
        generator.run_continuous(3)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
