#!/usr/bin/env python3
"""
Real-time data generator for TPB-Enhanced EWS simulation.
Generates realistic crowd data and updates the CSV file in real-time.
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

class RealTimeDataGenerator:
    def __init__(self, csv_file='ews_demo.csv'):
        self.csv_file = csv_file
        self.config = EWSConfig()
        self.alert_engine = AlertEngine(self.config)
        self.current_time = datetime.now()
        self.scenario_phase = "normal"
        self.scenario_intensity = 0.0  # 0.0 to 1.0
        
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
        
        # Simulate different scenarios
        scenarios = [
            {"name": "normal", "probability": 0.6, "intensity": 0.1},
            {"name": "morning_rush", "probability": 0.15, "intensity": 0.4},
            {"name": "evening_rush", "probability": 0.15, "intensity": 0.5},
            {"name": "festival_peak", "probability": 0.05, "intensity": 0.8},
            {"name": "emergency_situation", "probability": 0.05, "intensity": 0.9}
        ]
        
        # Choose scenario based on time and probability
        if 6 <= hour <= 10:  # Morning rush
            scenario = scenarios[1]
        elif 17 <= hour <= 21:  # Evening rush
            scenario = scenarios[2]
        elif random.random() < 0.1:  # Random festival peak
            scenario = scenarios[3]
        elif random.random() < 0.05:  # Random emergency
            scenario = scenarios[4]
        else:
            scenario = scenarios[0]
        
        self.scenario_phase = scenario["name"]
        self.scenario_intensity = scenario["intensity"]
        
        return scenario
    
    def generate_crowd_data(self):
        """Generate realistic crowd data based on current scenario"""
        scenario = self.generate_scenario()
        
        # Add more dynamic environmental conditions with higher fluctuation
        base_temp = 20 + 10 * np.sin(2 * np.pi * self.current_time.hour / 24)
        # Add more random variation and time-based fluctuations
        temp_variation = random.gauss(0, 4) + np.sin(2 * np.pi * self.current_time.minute / 60) * 2
        temp_c = base_temp + temp_variation + scenario["intensity"] * 8
        temp_c = max(5, min(40, temp_c))
        
        rh = 70 - (temp_c - 20) * 2 + random.gauss(0, 8) + np.cos(2 * np.pi * self.current_time.minute / 30) * 5
        rh = max(30, min(95, rh))
        
        thi_raw = thi_celsius(temp_c, rh)
        thi = normalize_thi(thi_raw)
        
        # Add time-based fluctuation factor for more dynamic data
        # Use both minute and second for more variation
        time_factor = (np.sin(2 * np.pi * self.current_time.minute / 15) + 
                      np.cos(2 * np.pi * self.current_time.second / 30)) * 0.4 + random.gauss(0, 0.3)
        
        # Crowd dynamics based on scenario with enhanced fluctuation
        if scenario["name"] == "emergency_situation":
            base_density = 4.0 + time_factor * 0.5
            density = base_density + random.gauss(0, 0.5)
            speed = 0.1 + random.gauss(0, 0.1) + time_factor * 0.05
            speed_var = 0.2 + random.gauss(0, 0.08) + abs(time_factor) * 0.05
            push_rate = 12 + random.gauss(0, 4) + abs(time_factor) * 3
            shout_rate = 20 + random.gauss(0, 6) + abs(time_factor) * 5
            near_falls = 8 + random.gauss(0, 3) + abs(time_factor) * 2
            
            ati = 0.9 + random.gauss(0, 0.08) + time_factor * 0.05
            sni = 0.95 + random.gauss(0, 0.05) + time_factor * 0.03
            pci = 0.05 + random.gauss(0, 0.05) - abs(time_factor) * 0.02
            
        elif scenario["name"] == "festival_peak":
            base_density = 3.5 + time_factor * 0.4
            density = base_density + random.gauss(0, 0.6)
            speed = 0.3 + random.gauss(0, 0.15) + time_factor * 0.1
            speed_var = 0.15 + random.gauss(0, 0.06) + abs(time_factor) * 0.04
            push_rate = 8 + random.gauss(0, 3) + abs(time_factor) * 2
            shout_rate = 15 + random.gauss(0, 4) + abs(time_factor) * 3
            near_falls = 5 + random.gauss(0, 2) + abs(time_factor) * 1.5
            
            ati = 0.8 + random.gauss(0, 0.12) + time_factor * 0.08
            sni = 0.85 + random.gauss(0, 0.1) + time_factor * 0.06
            pci = 0.2 + random.gauss(0, 0.1) - abs(time_factor) * 0.05
            
        elif scenario["name"] in ["morning_rush", "evening_rush"]:
            base_density = 2.5 + time_factor * 0.3
            density = base_density + random.gauss(0, 0.4)
            speed = 0.6 + random.gauss(0, 0.2) + time_factor * 0.1
            speed_var = 0.1 + random.gauss(0, 0.04) + abs(time_factor) * 0.03
            push_rate = 4 + random.gauss(0, 2) + abs(time_factor) * 1.5
            shout_rate = 8 + random.gauss(0, 3) + abs(time_factor) * 2
            near_falls = 2 + random.gauss(0, 1.5) + abs(time_factor) * 1
            
            ati = 0.6 + random.gauss(0, 0.18) + time_factor * 0.1
            sni = 0.7 + random.gauss(0, 0.12) + time_factor * 0.08
            pci = 0.4 + random.gauss(0, 0.12) - abs(time_factor) * 0.05
            
        else:  # normal
            base_density = 1.2 + time_factor * 0.2
            density = base_density + random.gauss(0, 0.3)
            speed = 1.0 + random.gauss(0, 0.15) + time_factor * 0.1
            speed_var = 0.04 + random.gauss(0, 0.02) + abs(time_factor) * 0.01
            push_rate = 0.8 + random.gauss(0, 0.6) + abs(time_factor) * 0.4
            shout_rate = 2 + random.gauss(0, 1.5) + abs(time_factor) * 1
            near_falls = 0.3 + random.gauss(0, 0.3) + abs(time_factor) * 0.2
            
            ati = 0.3 + random.gauss(0, 0.12) + time_factor * 0.08
            sni = 0.4 + random.gauss(0, 0.12) + time_factor * 0.06
            pci = 0.6 + random.gauss(0, 0.12) - abs(time_factor) * 0.05
        
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
        
        # Determine alert level using PHYSICAL risk (align with graph thresholds)
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
        self.df = self.df[present].copy()
        self.df.to_csv(self.csv_file, index=False)
    
    def run_simulation(self, duration_minutes=60, interval_seconds=5):
        """Run real-time simulation"""
        print(f"🚀 Starting TPB-Enhanced EWS Real-time Simulation")
        print(f"📊 Duration: {duration_minutes} minutes")
        print(f"⏱️  Update interval: {interval_seconds} seconds")
        print(f"📁 Data file: {self.csv_file}")
        print("-" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
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
                      f"Density: {new_data['density_p_m2']:.1f} | "
                      f"BI: {new_data['BI']:.3f}")
                
                # Wait for next update
                time.sleep(interval_seconds)
                
                # Advance time by the interval specified
                self.current_time += timedelta(seconds=interval_seconds)
        
        except KeyboardInterrupt:
            print("\n🛑 Simulation stopped by user")
        
        print(f"\n✅ Simulation completed!")
        print(f"📈 Generated {len(self.df)} data points")
        print(f"📊 Alert distribution: {self.df['Alert'].value_counts().to_dict()}")

def main():
    generator = RealTimeDataGenerator()
    
    print("TPB-Enhanced EWS Real-time Data Generator")
    print("=" * 50)
    print("This script generates realistic crowd data in real-time")
    print("and updates the CSV file for live dashboard visualization.")
    print()
    
    try:
        duration = int(input("Enter simulation duration in minutes (default 60): ") or "60")
        interval = int(input("Enter update interval in seconds (default 5): ") or "5")
        
        generator.run_simulation(duration, interval)
        
    except ValueError:
        print("Invalid input. Using default values.")
        generator.run_simulation(60, 5)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
