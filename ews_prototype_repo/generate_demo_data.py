#!/usr/bin/env python3
"""
Generate extended demo dataset for TPB-Enhanced EWS with realistic Simhasth 2028 scenarios.
Creates 7 days of data (2016 data points at 5-minute intervals) with TPB behavioral fields.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from ews_model import (
    EWSConfig, compute_cai, compute_cdi, normalize_thi, thi_celsius,
    normalize_ti, normalize_ei, compute_behavioral_intention, 
    compute_extended_risk, AlertEngine
)

def generate_realistic_scenarios():
    """Generate realistic scenarios for different phases of Simhasth 2028"""
    
    # Base configuration
    config = EWSConfig()
    alert_engine = AlertEngine(config)
    
    # Start time: 7 days before Shahi Snan
    start_time = datetime(2025, 1, 8, 0, 0)  # Start of Simhasth period
    end_time = start_time + timedelta(days=7)
    
    # Generate timestamps every 5 minutes
    timestamps = pd.date_range(start=start_time, end=end_time, freq='5min')
    n_points = len(timestamps)
    
    data = []
    
    for i, ts in enumerate(timestamps):
        hour = ts.hour
        day_of_event = (ts.date() - start_time.date()).days
        
        # Determine phase based on timing
        if day_of_event < 2:
            phase = "pre_event"
        elif day_of_event == 2:
            if 3 <= hour <= 10:  # Shahi Snan window
                phase = "shahi_snan"
            else:
                phase = "snan_window"
        elif day_of_event == 3:
            phase = "procession"
        else:
            phase = "post_event"
        
        # Generate realistic environmental conditions
        # Temperature varies by time of day and season
        base_temp = 15 + 8 * np.sin(2 * np.pi * hour / 24)  # Daily cycle
        temp_c = base_temp + random.gauss(0, 2)  # Add noise
        temp_c = max(5, min(35, temp_c))  # Clamp to realistic range
        
        # Humidity varies inversely with temperature
        rh = 80 - (temp_c - 15) * 2 + random.gauss(0, 5)
        rh = max(30, min(95, rh))
        
        # Compute THI
        thi_raw = thi_celsius(temp_c, rh)
        thi = normalize_thi(thi_raw)
        
        # Generate crowd dynamics based on phase and time
        if phase == "shahi_snan":
            # Peak density during Shahi Snan (3-10 AM)
            density = 3.5 + random.gauss(0, 0.5)  # Very high density
            speed = 0.2 + random.gauss(0, 0.1)    # Very slow movement
            speed_var = 0.15 + random.gauss(0, 0.05)  # High turbulence
            push_rate = 8 + random.gauss(0, 2)     # High anxiety signals
            shout_rate = 12 + random.gauss(0, 3)
            near_falls = 6 + random.gauss(0, 2)
            
            # High behavioral pressure during Shahi Snan
            ati = 0.8 + random.gauss(0, 0.1)      # Strong ritual attitude
            sni = 0.9 + random.gauss(0, 0.05)      # Very strong social pressure
            pci = 0.1 + random.gauss(0, 0.05)      # Very low perceived control
            
        elif phase == "snan_window":
            # Moderate density during other Snan periods
            density = 2.5 + random.gauss(0, 0.4)
            speed = 0.5 + random.gauss(0, 0.15)
            speed_var = 0.08 + random.gauss(0, 0.03)
            push_rate = 4 + random.gauss(0, 1.5)
            shout_rate = 6 + random.gauss(0, 2)
            near_falls = 2 + random.gauss(0, 1)
            
            ati = 0.6 + random.gauss(0, 0.15)
            sni = 0.7 + random.gauss(0, 0.1)
            pci = 0.3 + random.gauss(0, 0.1)
            
        elif phase == "procession":
            # Moving crowd during processions
            density = 2.0 + random.gauss(0, 0.3)
            speed = 0.8 + random.gauss(0, 0.2)
            speed_var = 0.12 + random.gauss(0, 0.04)
            push_rate = 3 + random.gauss(0, 1)
            shout_rate = 8 + random.gauss(0, 2)
            near_falls = 1 + random.gauss(0, 0.5)
            
            ati = 0.5 + random.gauss(0, 0.1)
            sni = 0.6 + random.gauss(0, 0.1)
            pci = 0.4 + random.gauss(0, 0.1)
            
        else:  # pre_event, post_event
            # Normal crowd conditions
            density = 1.0 + random.gauss(0, 0.2)
            speed = 1.0 + random.gauss(0, 0.1)
            speed_var = 0.03 + random.gauss(0, 0.01)
            push_rate = 0.5 + random.gauss(0, 0.3)
            shout_rate = 1 + random.gauss(0, 0.5)
            near_falls = 0.2 + random.gauss(0, 0.1)
            
            ati = 0.2 + random.gauss(0, 0.1)
            sni = 0.3 + random.gauss(0, 0.1)
            pci = 0.7 + random.gauss(0, 0.1)
        
        # Clamp values to realistic ranges
        density = max(0.1, min(5.0, density))
        speed = max(0.05, min(1.5, speed))
        speed_var = max(0.01, min(0.3, speed_var))
        push_rate = max(0, min(15, push_rate))
        shout_rate = max(0, min(25, shout_rate))
        near_falls = max(0, min(10, near_falls))
        ati = max(0, min(1, ati))
        sni = max(0, min(1, sni))
        pci = max(0, min(1, pci))
        
        # Compute indices
        cai = compute_cai(push_rate, shout_rate, near_falls, density)
        cdi = compute_cdi(density, speed, speed_var)
        ti = normalize_ti(hour)
        ei = normalize_ei(phase)
        
        # Compute behavioral intention
        bi = compute_behavioral_intention(ati, sni, pci)
        
        # Compute risks
        physical_risk = config.weights["CAI"]*cai + config.weights["CDI"]*cdi + \
                       config.weights["THI"]*thi + config.weights["TI"]*ti + \
                       config.weights["EI"]*ei
        risk_extended = compute_extended_risk(cai, cdi, thi, ti, ei, ati, sni, pci, config.weights)
        
        # Determine alert level using extended risk
        alert = alert_engine.step(risk_extended)
        
        data.append({
            'timestamp': ts,
            'phase': phase,
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
            'RiskExtended': round(risk_extended, 3),
            'Alert': alert
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Generating extended demo dataset for TPB-Enhanced EWS...")
    df = generate_realistic_scenarios()
    
    # Save to CSV
    df.to_csv('ews_demo_extended.csv', index=False)
    print(f"Generated {len(df)} data points")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Phases: {df['phase'].unique()}")
    print(f"Alert distribution: {df['Alert'].value_counts().to_dict()}")
    
    # Show sample of high-risk scenarios
    high_risk = df[df['RiskExtended'] > 0.6].head(10)
    print(f"\nSample high-risk scenarios (RiskExtended > 0.6):")
    print(high_risk[['timestamp', 'phase', 'RiskExtended', 'Alert', 'ATI', 'SNI', 'PCI', 'BI']].to_string())

