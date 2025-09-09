# TPB-Enhanced Early Warning System (EWS) for Simhasth 2028

A comprehensive crowd management system that combines physical monitoring with behavioral psychology (Theory of Planned Behavior) to predict and prevent crowd-related incidents.

## 🚀 Features

- **TPB-Enhanced Risk Assessment**: Combines physical indices (CAI, CDI, THI, TI, EI) with behavioral intention (BI)
- **Real-time Monitoring**: Live dashboard with beautiful UI and real-time data visualization
- **Alert System**: Four-level alert system (Green, Yellow, Orange, Red) with hysteresis
- **Simulation Mode**: Real-time data generator for testing and demonstration
- **Interactive Charts**: Real-time risk visualization with proper axis labels and thresholds

## 📊 System Components

### Physical Indices
- **CAI (Crowd Anxiety Index)**: Measures stress, fear, and restlessness
- **CDI (Crowd Dynamics Index)**: Evaluates flow stability and turbulence
- **THI (Temperature-Humidity Index)**: Heat stress assessment
- **TI (Time Index)**: Temporal criticality during peak hours
- **EI (Event Index)**: Ritual and procession surge intensity

### Behavioral Component (TPB)
- **ATI (Attitude)**: Belief that ritual success requires immediate participation
- **SNI (Subjective Norms)**: Pressure to imitate majority's movement
- **PCI (Perceived Control)**: Feeling of being able to stop/pause/exit safely
- **BI (Behavioral Intention)**: Combined psychological readiness for risky movement

### Extended Risk Formula
```
RiskExtended = 0.6 × (DANP-weighted physical indices) + 0.4 × BI
```

## 🛠️ Installation & Setup

1. **Clone/Download the repository**
2. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the System

### Option 1: Complete System (Recommended)
```bash
python run_ews_system.py
```
This starts both the Flask server and real-time data generator.

### Option 2: Continuous Data Generation (No Stuck Data)
```bash
python continuous_data_generator.py
```
Starts continuous data generation that never gets stuck, perfect for live demos.

### Option 3: Individual Components

**Start Flask Server Only**:
```bash
python app.py
```
Access dashboard at: http://127.0.0.1:8000

**Start Data Generator Only**:
```bash
python realtime_data_generator.py
```

**Generate Demo Dataset**:
```bash
python generate_demo_data.py
```

## 📱 Dashboard Features

### Real-time Dashboard
- **Live Status**: Current risk levels and alert status with dynamic updates
- **Metric Cards**: All physical and behavioral indices with animation effects
- **Interactive Chart**: Real-time risk visualization with:
  - Physical Risk (blue line)
  - Extended Risk (red line)
  - Alert thresholds (Yellow, Orange, Red)
  - Proper axis labels (Risk Level vs Time)
  - Dynamic data points with color-coded alerts
- **Visual Effects**: 
  - Animated metric updates when values change
  - Chart shimmer effect for live data indication
  - Pulsing status indicators
  - Smooth transitions and hover effects

### Controls
- **Real-Time Mode**: Live data streaming (2-second updates)
- **Historical Mode**: View past data
- **Download Data**: Export current session data
- **Reset Chart**: Clear visualization

## 📊 API Endpoints

- `GET /` - Main dashboard
- `GET /status` - Current system status with all indices
- `GET /history?n=288` - Historical data (default: 24h at 5-min intervals)
- `GET /download/<filename>` - Download data files

## 🎯 Alert Levels

| Level | Risk Range | Description | Action Required |
|-------|------------|-------------|-----------------|
| 🟢 Green | 0.0 - 0.4 | Normal, safe conditions | Monitor |
| 🟡 Yellow | 0.4 - 0.6 | Early warning | Increase monitoring |
| 🟠 Orange | 0.6 - 0.75 | High risk | Deploy interventions |
| 🔴 Red | > 0.75 | Critical | Immediate dispersal |

## 🔬 Simulation Scenarios

The real-time generator simulates various crowd scenarios:

- **Normal**: Regular crowd conditions
- **Morning Rush**: Peak morning hours
- **Evening Rush**: Peak evening hours  
- **Festival Peak**: High-intensity religious events
- **Emergency Situation**: Critical crowd incidents

## 📈 Data Structure

Each data point includes:
```json
{
  "timestamp": "2025-01-15T00:05:00",
  "phase": "normal",
  "temp_c": 22.5,
  "rh": 65.0,
  "THI": 0.123,
  "density_p_m2": 1.2,
  "speed_mps": 1.0,
  "CAI": 0.136,
  "CDI": 0.175,
  "THI": 0.0,
  "TI": 0.2,
  "EI": 0.2,
  "ATI": 0.233,
  "SNI": 0.468,
  "PCI": 0.655,
  "BI": 0.435,
  "Risk": 0.156,
  "RiskExtended": 0.268,
  "Alert": "green"
}
```

## 🎨 UI Features

- **Beautiful Gradient Design**: Modern, professional appearance
- **Responsive Layout**: Works on different screen sizes
- **Real-time Indicators**: Live status indicators and animations
- **Interactive Charts**: Canvas-based visualization with proper scaling
- **Color-coded Alerts**: Visual alert level indicators

## 🔧 Customization

### Modify Alert Thresholds
Edit `ews_model.py`:
```python
thresholds = {
    "yellow": 0.40,
    "orange": 0.60,
    "red": 0.75
}
```

### Adjust TPB Weights
Modify behavioral intention calculation:
```python
def compute_behavioral_intention(ATI, SNI, PCI):
    return clamp01(0.3*ATI + 0.5*SNI + 0.2*PCI)
```

### Change Update Intervals
Modify JavaScript in `static/index.html`:
```javascript
setInterval(fetchStatus, 5000);  // 5 seconds
```

## 📝 Files Overview

- `app.py` - Flask web server
- `ews_model.py` - Core EWS algorithms and TPB calculations
- `static/index.html` - Beautiful dashboard UI
- `realtime_data_generator.py` - Real-time data simulation
- `generate_demo_data.py` - Generate large demo datasets
- `run_ews_system.py` - System launcher
- `ews_demo.csv` - Demo data file
- `requirements.txt` - Python dependencies

## 🌟 Key Innovations

1. **TPB Integration**: First EWS to incorporate behavioral psychology
2. **Extended Risk Index**: Combines physical and psychological factors
3. **Real-time Simulation**: Live data generation for testing
4. **Beautiful UI**: Professional dashboard with modern design
5. **Hysteresis Logic**: Prevents alert flickering

## 🚨 Emergency Use

For actual deployment at Simhasth 2028:
1. Replace simulation data with real IoT sensors
2. Integrate with district command center
3. Connect to intervention systems
4. Train operators on TPB concepts
5. Establish communication protocols

## 📞 Support

This is a prototype system for research and demonstration purposes. For production deployment, additional safety measures and validation are required.

---

**TPB-Enhanced Early Warning System for Simhasth 2028**  
*Preventing crowd incidents through psychological insights*


*To run this project please run these command*
chmod +x continuous_data_generator.py
source .venv/bin/activate && python continuous_data_generator.py

python3 app.py

*To kill data generator*
pkill -f continuous_data_generator.py

