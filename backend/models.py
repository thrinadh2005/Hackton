from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime
from datetime import datetime
from .database import Base

class EVTelemetry(Base):
    __tablename__ = "ev_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    voltage = Column(Float)
    current = Column(Float)
    temperature = Column(Float)
    vibration_x = Column(Float)
    vibration_y = Column(Float)
    vibration_z = Column(Float)
    predicted_soh = Column(Float)
    anomaly_score = Column(Float)
    is_anomaly = Column(Boolean, default=False)
    fault_type = Column(String, default="Normal")

class IndustrialReport(Base):
    __tablename__ = "industrial_reports"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    check_type = Column(String)  # "wire_harness" or "weld_electrode"
    
    # Wire Harness parameters
    connector_type = Column(String, nullable=True)
    camera_confidence = Column(Float, nullable=True)  # YOLO verification
    click_acoustic_peak = Column(Float, nullable=True) # Decibel/Frequency peak
    click_duration_ms = Column(Float, nullable=True)
    click_status = Column(String, nullable=True)  # "PASS" or "FAIL"
    
    # Weld Electrode parameters
    cycle_count = Column(Integer, nullable=True)
    weld_current_ka = Column(Float, nullable=True)
    spatter_level = Column(Float, nullable=True)      # Metric representing electrode wear
    electrode_health = Column(Float, nullable=True)   # Percent health remaining
    
    status = Column(String, default="Normal")  # "Normal", "Fail", "Wear Warning"

class SupplyChainEvent(Base):
    __tablename__ = "supply_chain_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    supplier_id = Column(String)
    material = Column(String)
    geopolitical_risk_score = Column(Float)
    material_scarcity_index = Column(Float)
    supplier_defect_rate = Column(Float)
    lead_time_days = Column(Float)
    risk_score = Column(Integer)  # 1 for High Risk, 0 for Low Risk
    status = Column(String, default="Stable")

class FleetReadiness(Base):
    __tablename__ = "fleet_readiness"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    vehicle_id = Column(String)
    route_distance_km = Column(Float)
    payload_tons = Column(Float)
    duty_cycle_hours = Column(Float)
    readiness_score = Column(Float)
    carbon_saved_kg = Column(Float)  # Hypothetical tracking of Scope 1/3 emissions avoided
