
import math
from typing import Dict, Tuple

class EWSConfig:
    """
    Configuration for the Early Warning System (weights, thresholds, hysteresis).
    DANP limit weights (from prior step):
        EI  = 0.24063
        CDI = 0.22613
        TI  = 0.21530
        CAI = 0.18841
        THI = 0.12954
    """
    weights = {
        "CAI": 0.18841,
        "CDI": 0.22613,
        "THI": 0.12954,
        "TI":  0.21530,
        "EI":  0.24063
    }
    # Alert thresholds
    thresholds = {
        "yellow": 0.40,
        "orange": 0.60,
        "red":    0.75
    }
    # Hysteresis: number of consecutive steps required before changing level
    hysteresis_up   = {"green->yellow": 2, "yellow->orange": 2, "orange->red": 1}
    hysteresis_down = {"red->orange": 2, "orange->yellow": 2, "yellow->green": 2}


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def sigmoid(x: float, k: float = 8.0, x0: float = 0.5) -> float:
    """
    Smooth mapping to [0,1], centered at x0 with steepness k.
    """
    return 1.0 / (1.0 + math.exp(-k*(x - x0)))


def thi_celsius(temp_c: float, rh: float) -> float:
    """
    Temperature-Humidity Index (approximate, Celsius): 
    THI = T - (0.55 - 0.0055*RH)*(T - 14.5)
    where RH is in [0,100].
    Returns a raw THI in Celsius-like units, typically ~15-40.
    """
    return temp_c - (0.55 - 0.0055*rh) * (temp_c - 14.5)


def normalize_thi(thi: float) -> float:
    """
    Map THI to 0..1 risk. Below ~22 is comfortable; above ~30 is stressful.
    """
    return clamp01((thi - 22.0) / (32.0 - 22.0))


def normalize_density(pers_per_m2: float) -> float:
    """
    Crowd density risk mapping (Fruin-inspired bands):
      <1.0: low, 1-2: moderate, 2-3.5: high, >3.5: severe.
    """
    if pers_per_m2 <= 1.0: 
        return 0.15 * (pers_per_m2 / 1.0)
    if pers_per_m2 <= 2.0:
        return 0.15 + 0.25 * ((pers_per_m2 - 1.0) / 1.0)
    if pers_per_m2 <= 3.5:
        return 0.40 + 0.35 * ((pers_per_m2 - 2.0) / 1.5)
    # >3.5
    return 0.75 + 0.25 * min(1.0, (pers_per_m2 - 3.5) / 1.5)


def normalize_speed(speed_mps: float) -> float:
    """
    Lower average speed (congestion) -> higher risk.
    Assume nominal free-flow ~1.2 m/s; <0.3 m/s is near-stall.
    """
    speed = max(0.0, min(1.2, speed_mps))
    return 1.0 - (speed / 1.2)


def normalize_speed_var(var_mps2: float) -> float:
    """
    High speed variance / turbulence indicates unstable dynamics.
    Normalize w.r.t a practical band 0..0.5 (m/s)^2.
    """
    return clamp01(var_mps2 / 0.5)


def compute_cdi(density: float, speed: float, speed_var: float) -> float:
    """
    Crowd Dynamics Index (0..1) from density, speed, speed variance.
    We combine with weights emphasizing density & instability.
    """
    dn = normalize_density(density)
    sn = normalize_speed(speed)
    vn = normalize_speed_var(speed_var)
    # Emphasize density 50%, turbulence 30%, low speed 20%
    return clamp01(0.5*dn + 0.3*vn + 0.2*sn)


def normalize_anxiety_signals(push_rate: float, shout_rate: float, near_falls: float) -> float:
    """
    CAI proxy from discrete signals:
      - push_rate: pushes per minute per 1000 people (0..10 typical)
      - shout_rate: shouts per minute per 1000 people (0..20 typical)
      - near_falls: near-fall incidents per 5-min window (0..10 typical)
    """
    pr = clamp01(push_rate / 10.0)
    sr = clamp01(shout_rate / 20.0)
    nf = clamp01(near_falls / 10.0)
    return clamp01(0.4*pr + 0.3*sr + 0.3*nf)


def compute_cai(push_rate: float, shout_rate: float, near_falls: float, density: float) -> float:
    """
    CAI combines anxiety signals and amplifies with density (since anxiety at high density is riskier).
    """
    base = normalize_anxiety_signals(push_rate, shout_rate, near_falls)
    amp = 0.25 * normalize_density(density)
    return clamp01(base + amp)


def normalize_ti(hour: int, risk_windows: Dict[str, Tuple[int,int]] = None) -> float:
    """
    Time Index: higher during known peak windows (e.g., Shahi Snan morning hours).
    Tuned for gentler contribution so more time stays in green under normal conditions.
    """
    if risk_windows is None:
        risk_windows = {
            "pre_dawn": (3, 6),
            "morning":  (6, 10),
            "evening":  (17, 20)
        }
    score = 0.1  # lower base
    for (start,end) in risk_windows.values():
        if start <= hour < end:
            score += 0.5  # gentler than 0.6
    # Shoulder hours near peaks get a small bump
    if any(abs(hour - h) == 1 for h in [3,6,10,17,20]):
        score += 0.1
    return clamp01(score)


def normalize_ei(phase: str) -> float:
    """
    Event Index by ritual/phase.

    Note: Real-time generators use scenario names like
    "morning_rush", "evening_rush", "festival_peak", "emergency_situation".
    Map those explicitly so EI contributes appropriately and red alerts are
    achievable during critical scenarios.
    """
    phase = (phase or "").lower()
    mapping = {
        # Baseline phases
        "normal": 0.15,
        "pre_event": 0.15,
        "post_event": 0.25,
        "snan_window": 0.65,
        "shahi_snan": 0.9,
        "procession": 0.7,

        # Real-time/continuous simulator scenarios (gentler except critical ones)
        "morning_rush": 0.45,
        "evening_rush": 0.5,
        "festival_peak": 0.8,
        "emergency_situation": 0.95,
    }
    return mapping.get(phase, 0.2)


def composite_risk(CAI: float, CDI: float, THI: float, TI: float, EI: float, weights: Dict[str, float]) -> float:
    """
    Weighted sum risk score using DANP weights.
    Inputs must be in 0..1.
    """
    return clamp01(
        weights["CAI"]*CAI +
        weights["CDI"]*CDI +
        weights["THI"]*THI +
        weights["TI"] *TI  +
        weights["EI"] *EI
    )


def compute_behavioral_intention(ATI: float, SNI: float, PCI: float) -> float:
    """
    Theory of Planned Behavior (TPB) Behavioral Intention computation.
    BI = 0.3*ATI + 0.5*SNI + 0.2*PCI
    
    ATI (Attitude): Belief that ritual success requires immediate participation (0..1)
    SNI (Subjective Norms): Pressure to imitate majority's movement (0..1) 
    PCI (Perceived Control): Feeling of being able to stop/pause/exit safely (0..1)
    
    For Simhasth 2028: Norms (β=0.5) dominate due to herd behavior,
    while Control (γ=0.2) is weaker because of crowd density.
    """
    return clamp01(0.3*ATI + 0.5*SNI + 0.2*PCI)


def compute_extended_risk(CAI: float, CDI: float, THI: float, TI: float, EI: float, 
                        ATI: float, SNI: float, PCI: float, weights: Dict[str, float]) -> float:
    """
    TPB-Enhanced Extended Risk Index.
    RiskExtended = 0.6*(DANP-weighted physical indices) + 0.4*BI
    
    0.6 weight → Physical-psychological indices
    0.4 weight → Behavioral intention (BI)
    """
    physical_risk = composite_risk(CAI, CDI, THI, TI, EI, weights)
    behavioral_intention = compute_behavioral_intention(ATI, SNI, PCI)
    
    return clamp01(0.6*physical_risk + 0.4*behavioral_intention)


class AlertEngine:
    """
    Hysteresis-based alert state machine.
    Levels: green < yellow < orange < red
    """
    def __init__(self, cfg: EWSConfig = EWSConfig()):
        self.cfg = cfg
        self.state = "green"
        self.counters = {"up":0, "down":0}

    def step(self, risk: float) -> str:
        th = self.cfg.thresholds
        prev = self.state

        # Decide desired level from instantaneous risk
        desired = "green"
        if risk >= th["red"]:
            desired = "red"
        elif risk >= th["orange"]:
            desired = "orange"
        elif risk >= th["yellow"]:
            desired = "yellow"

        # Hysteresis logic
        if desired == prev:
            self.counters = {"up":0, "down":0}
            return self.state

        # Moving up?
        levels = ["green","yellow","orange","red"]
        if levels.index(desired) > levels.index(prev):
            self.counters["up"] += 1
            self.counters["down"] = 0
            key = f"{prev}->{desired}"
            need = self.cfg.hysteresis_up.get(key, 1)
            if self.counters["up"] >= need:
                self.state = desired
                self.counters = {"up":0, "down":0}
        else:
            # Moving down
            self.counters["down"] += 1
            self.counters["up"] = 0
            key = f"{prev}->{desired}"
            need = self.cfg.hysteresis_down.get(key, 1)
            if self.counters["down"] >= need:
                self.state = desired
                self.counters = {"up":0, "down":0}

        return self.state
