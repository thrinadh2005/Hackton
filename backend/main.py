import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import joblib
import numpy as np

import torch
import torch.nn as nn
from transformers import pipeline

from .database import engine, Base, get_db
from .models import EVTelemetry, IndustrialReport, SupplyChainEvent, FleetReadiness

app = FastAPI(title="EdgeIntel-AM API Gateway", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

fault_state = {
    "battery_fault": False,
    "motor_fault": False,
    "harness_fault": False,
    "electrode_fault": False,
    "supply_chain_fault": False,
    "fleet_fault": False
}

models = {}

# PyTorch Model Definitions
class TabularMLP(nn.Module):
    def __init__(self, input_dim, output_dim=1, is_classification=False):
        super().__init__()
        self.is_classification = is_classification
        self.net = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, output_dim)
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.net(x)
        if self.is_classification:
            return self.sigmoid(out)
        return out

class AnomalyAutoencoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 8),
            nn.ReLU(),
            nn.Linear(8, 3),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(3, 8),
            nn.ReLU(),
            nn.Linear(8, input_dim)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

# GenAI Initialization
try:
    print("Loading Gen AI Model (HuggingFace Transformers)...")
    genai_pipeline = pipeline("text-generation", model="distilgpt2", max_new_tokens=25, pad_token_id=50256)
    print("Gen AI Model Loaded.")
except Exception as e:
    genai_pipeline = None
    print(f"Gen AI load failed: {e}")

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    try:
        models["ev_soh_scaler"] = joblib.load("models/ev_soh_model_scaler.pkl")
        models["ev_soh"] = TabularMLP(4)
        models["ev_soh"].load_state_dict(torch.load("models/ev_soh_model.pth"))
        models["ev_soh"].eval()

        models["ev_motor_anomaly_scaler"] = joblib.load("models/ev_motor_anomaly_scaler.pkl")
        motor_data = torch.load("models/ev_motor_anomaly_model.pth")
        models["ev_motor_anomaly"] = AnomalyAutoencoder(3)
        models["ev_motor_anomaly"].load_state_dict(motor_data['state_dict'])
        models["ev_motor_anomaly"].eval()
        models["ev_motor_anomaly_threshold"] = motor_data['threshold']

        models["industrial_click_scaler"] = joblib.load("models/industrial_click_model_scaler.pkl")
        models["industrial_click"] = TabularMLP(3, is_classification=True)
        models["industrial_click"].load_state_dict(torch.load("models/industrial_click_model.pth"))
        models["industrial_click"].eval()

        models["weld_electrode_scaler"] = joblib.load("models/weld_electrode_health_model_scaler.pkl")
        models["weld_electrode"] = TabularMLP(3)
        models["weld_electrode"].load_state_dict(torch.load("models/weld_electrode_health_model.pth"))
        models["weld_electrode"].eval()

        models["supply_chain_risk_scaler"] = joblib.load("models/supply_chain_risk_model_scaler.pkl")
        models["supply_chain_risk"] = TabularMLP(4, is_classification=True)
        models["supply_chain_risk"].load_state_dict(torch.load("models/supply_chain_risk_model.pth"))
        models["supply_chain_risk"].eval()

        models["fleet_readiness_scaler"] = joblib.load("models/fleet_readiness_model_scaler.pkl")
        models["fleet_readiness"] = TabularMLP(3)
        models["fleet_readiness"].load_state_dict(torch.load("models/fleet_readiness_model.pth"))
        models["fleet_readiness"].eval()
        print("All Deep Learning models loaded successfully.")
    except Exception as e:
        print(f"Error loading DL models: {e}")

@app.get("/")
def read_root():
    return {"status": "online", "models_loaded": list(models.keys())}

@app.get("/api/fault/states")
def get_fault_states():
    return fault_state

@app.post("/api/fault/inject")
def inject_fault(state: Dict[str, bool]):
    global fault_state
    for k in state:
        if k in fault_state:
            fault_state[k] = state[k]
    return {"status": "updated", "states": fault_state}

@app.post("/api/telemetry/ev")
async def log_ev_telemetry(data: Dict[str, Any], db: Session = Depends(get_db)):
    voltage = data.get("voltage", 3.7)
    current = data.get("current", 1.5)
    temp = data.get("temperature", 25.0)
    cycles = data.get("cycles", 100)
    vib_x = data.get("vibration_x", 0.0)
    vib_y = data.get("vibration_y", 0.0)
    vib_z = data.get("vibration_z", 0.0)
    
    predicted_soh = 100.0
    if "ev_soh" in models:
        try:
            X_scaled = models["ev_soh_scaler"].transform([[voltage, current, temp, cycles]])
            with torch.no_grad():
                pred = models["ev_soh"](torch.tensor(X_scaled, dtype=torch.float32))
            predicted_soh = float(pred[0][0])
        except Exception:
            pass
            
    anomaly_score = 1.0
    is_anomaly = False
    if "ev_motor_anomaly" in models:
        try:
            X_scaled = models["ev_motor_anomaly_scaler"].transform([[vib_x, vib_y, vib_z]])
            t_scaled = torch.tensor(X_scaled, dtype=torch.float32)
            with torch.no_grad():
                reconstructed = models["ev_motor_anomaly"](t_scaled)
                mse = torch.mean((t_scaled - reconstructed)**2).item()
            is_anomaly = bool(mse > models["ev_motor_anomaly_threshold"])
            anomaly_score = float(mse)
            
            if is_anomaly and genai_pipeline:
                prompt = f"Motor vibration anomaly detected (MSE {mse:.2f}). Expert Advice:"
                res = genai_pipeline(prompt)
                ai_insight = res[0]['generated_text'].replace(prompt, "").strip()
                await manager.broadcast({"type": "genai_insight", "data": {"context": "Motor Anomaly", "insight": ai_insight}})
        except Exception:
            pass

    db_entry = EVTelemetry(
        voltage=voltage, current=current, temperature=temp,
        vibration_x=vib_x, vibration_y=vib_y, vibration_z=vib_z,
        predicted_soh=predicted_soh, anomaly_score=anomaly_score,
        is_anomaly=is_anomaly, fault_type=data.get("fault_type", "Normal")
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    payload = {
        "type": "ev",
        "data": {
            "id": db_entry.id, "timestamp": db_entry.timestamp.isoformat(),
            "voltage": db_entry.voltage, "current": db_entry.current, "temperature": db_entry.temperature,
            "vibration_x": db_entry.vibration_x, "vibration_y": db_entry.vibration_y, "vibration_z": db_entry.vibration_z,
            "predicted_soh": db_entry.predicted_soh, "anomaly_score": db_entry.anomaly_score,
            "is_anomaly": db_entry.is_anomaly, "fault_type": db_entry.fault_type
        }
    }
    await manager.broadcast(payload)
    return {"status": "saved", "id": db_entry.id}

@app.post("/api/telemetry/industrial")
async def log_industrial_report(data: Dict[str, Any], db: Session = Depends(get_db)):
    check_type = data.get("check_type")
    
    if check_type == "wire_harness":
        freq = data.get("click_acoustic_peak", 3000.0)
        db_level = data.get("decibels", 75.0)
        duration = data.get("click_duration_ms", 25.0)
        camera_conf = data.get("camera_confidence", 0.98)
        
        click_status = "FAIL"
        if "industrial_click" in models:
            try:
                X_scaled = models["industrial_click_scaler"].transform([[freq, db_level, duration]])
                with torch.no_grad():
                    pred = models["industrial_click"](torch.tensor(X_scaled, dtype=torch.float32))
                click_status = "PASS" if float(pred[0][0]) > 0.5 else "FAIL"
            except Exception:
                pass
                
        status = "Normal" if (click_status == "PASS" and camera_conf >= 0.85) else "Fail"
        
        db_entry = IndustrialReport(
            check_type="wire_harness", connector_type=data.get("connector_type", "TATA-C100"),
            camera_confidence=camera_conf, click_acoustic_peak=freq, click_duration_ms=duration,
            click_status=click_status, status=status
        )
    elif check_type == "weld_electrode":
        cycle_count = data.get("cycle_count", 1000)
        weld_curr = data.get("weld_current_ka", 11.2)
        spatter = data.get("spatter_level", 2.0)
        
        health = 100.0
        if "weld_electrode" in models:
            try:
                X_scaled = models["weld_electrode_scaler"].transform([[cycle_count, weld_curr, spatter]])
                with torch.no_grad():
                    pred = models["weld_electrode"](torch.tensor(X_scaled, dtype=torch.float32))
                health = float(pred[0][0])
            except Exception:
                pass
                
        status = "Normal"
        if health < 30.0:
            status = "Wear Warning"
            if genai_pipeline:
                prompt = f"Welding electrode health dropped to {health:.1f}%. Action required:"
                res = genai_pipeline(prompt)
                ai_insight = res[0]['generated_text'].replace(prompt, "").strip()
                await manager.broadcast({"type": "genai_insight", "data": {"context": "Electrode Wear", "insight": ai_insight}})

        if health < 10.0:
            status = "Fail"
            
        db_entry = IndustrialReport(
            check_type="weld_electrode", cycle_count=cycle_count, weld_current_ka=weld_curr,
            spatter_level=spatter, electrode_health=health, status=status
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid check type")
        
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    payload = {
        "type": "industrial",
        "data": {
            "id": db_entry.id, "timestamp": db_entry.timestamp.isoformat(),
            "check_type": db_entry.check_type, "connector_type": db_entry.connector_type,
            "camera_confidence": db_entry.camera_confidence, "click_acoustic_peak": db_entry.click_acoustic_peak,
            "click_status": db_entry.click_status, "cycle_count": db_entry.cycle_count,
            "weld_current_ka": db_entry.weld_current_ka, "spatter_level": db_entry.spatter_level,
            "electrode_health": db_entry.electrode_health, "status": db_entry.status
        }
    }
    await manager.broadcast(payload)
    return {"status": "saved", "id": db_entry.id}

@app.post("/api/telemetry/supply_chain")
async def log_supply_chain_event(data: Dict[str, Any], db: Session = Depends(get_db)):
    geo = data.get("geopolitical_risk_score", 1.0)
    scarcity = data.get("material_scarcity_index", 1.0)
    defect = data.get("supplier_defect_rate", 0.5)
    lead = data.get("lead_time_days", 14.0)
    
    risk_score = 0
    status = "Stable"
    if "supply_chain_risk" in models:
        try:
            X_scaled = models["supply_chain_risk_scaler"].transform([[geo, scarcity, defect, lead]])
            with torch.no_grad():
                pred = models["supply_chain_risk"](torch.tensor(X_scaled, dtype=torch.float32))
            risk_score = 1 if float(pred[0][0]) > 0.5 else 0
            if risk_score == 1:
                status = "High Risk"
                if genai_pipeline:
                    prompt = f"Supply chain disruption for {data.get('material', 'Lithium')} detected. Mitigation strategy:"
                    res = genai_pipeline(prompt)
                    ai_insight = res[0]['generated_text'].replace(prompt, "").strip()
                    await manager.broadcast({"type": "genai_insight", "data": {"context": "Supply Chain Risk", "insight": ai_insight}})
        except Exception:
            pass
            
    db_entry = SupplyChainEvent(
        supplier_id=data.get("supplier_id", "SUP-UNKNOWN"), material=data.get("material", "Lithium"),
        geopolitical_risk_score=geo, material_scarcity_index=scarcity,
        supplier_defect_rate=defect, lead_time_days=lead,
        risk_score=risk_score, status=status
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    payload = {
        "type": "supply_chain",
        "data": {
            "id": db_entry.id, "timestamp": db_entry.timestamp.isoformat(),
            "supplier_id": db_entry.supplier_id, "material": db_entry.material,
            "geopolitical_risk_score": db_entry.geopolitical_risk_score, "material_scarcity_index": db_entry.material_scarcity_index,
            "supplier_defect_rate": db_entry.supplier_defect_rate, "lead_time_days": db_entry.lead_time_days,
            "risk_score": db_entry.risk_score, "status": db_entry.status
        }
    }
    await manager.broadcast(payload)
    return {"status": "saved", "id": db_entry.id}

@app.post("/api/telemetry/fleet")
async def log_fleet_readiness(data: Dict[str, Any], db: Session = Depends(get_db)):
    dist = data.get("route_distance_km", 100.0)
    payload_t = data.get("payload_tons", 10.0)
    duty = data.get("duty_cycle_hours", 8.0)
    
    readiness = 0.0
    if "fleet_readiness" in models:
        try:
            X_scaled = models["fleet_readiness_scaler"].transform([[dist, payload_t, duty]])
            with torch.no_grad():
                pred = models["fleet_readiness"](torch.tensor(X_scaled, dtype=torch.float32))
            readiness = float(pred[0][0])
        except Exception:
            pass
            
    db_entry = FleetReadiness(
        vehicle_id=data.get("vehicle_id", "V-000"), route_distance_km=dist,
        payload_tons=payload_t, duty_cycle_hours=duty,
        readiness_score=readiness, carbon_saved_kg=data.get("carbon_saved_kg", 0.0)
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    payload = {
        "type": "fleet",
        "data": {
            "id": db_entry.id, "timestamp": db_entry.timestamp.isoformat(),
            "vehicle_id": db_entry.vehicle_id, "route_distance_km": db_entry.route_distance_km,
            "payload_tons": db_entry.payload_tons, "duty_cycle_hours": db_entry.duty_cycle_hours,
            "readiness_score": db_entry.readiness_score, "carbon_saved_kg": db_entry.carbon_saved_kg
        }
    }
    await manager.broadcast(payload)
    return {"status": "saved", "id": db_entry.id}

@app.get("/api/history/ev", response_model=List[Dict[str, Any]])
def get_ev_history(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(EVTelemetry).order_by(EVTelemetry.timestamp.desc()).limit(limit).all()
    return [{"id": r.id, "timestamp": r.timestamp.isoformat(), "voltage": r.voltage, "current": r.current, "temperature": r.temperature, "vibration_x": r.vibration_x, "vibration_y": r.vibration_y, "vibration_z": r.vibration_z, "predicted_soh": r.predicted_soh, "anomaly_score": r.anomaly_score, "is_anomaly": r.is_anomaly, "fault_type": r.fault_type} for r in records]

@app.get("/api/history/industrial", response_model=List[Dict[str, Any]])
def get_industrial_history(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(IndustrialReport).order_by(IndustrialReport.timestamp.desc()).limit(limit).all()
    return [{"id": r.id, "timestamp": r.timestamp.isoformat(), "check_type": r.check_type, "connector_type": r.connector_type, "camera_confidence": r.camera_confidence, "click_acoustic_peak": r.click_acoustic_peak, "click_status": r.click_status, "cycle_count": r.cycle_count, "weld_current_ka": r.weld_current_ka, "spatter_level": r.spatter_level, "electrode_health": r.electrode_health, "status": r.status} for r in records]

@app.get("/api/history/supply_chain", response_model=List[Dict[str, Any]])
def get_supply_chain_history(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(SupplyChainEvent).order_by(SupplyChainEvent.timestamp.desc()).limit(limit).all()
    return [{"id": r.id, "timestamp": r.timestamp.isoformat(), "supplier_id": r.supplier_id, "material": r.material, "geopolitical_risk_score": r.geopolitical_risk_score, "material_scarcity_index": r.material_scarcity_index, "supplier_defect_rate": r.supplier_defect_rate, "lead_time_days": r.lead_time_days, "risk_score": r.risk_score, "status": r.status} for r in records]

@app.get("/api/history/fleet", response_model=List[Dict[str, Any]])
def get_fleet_history(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(FleetReadiness).order_by(FleetReadiness.timestamp.desc()).limit(limit).all()
    return [{"id": r.id, "timestamp": r.timestamp.isoformat(), "vehicle_id": r.vehicle_id, "route_distance_km": r.route_distance_km, "payload_tons": r.payload_tons, "duty_cycle_hours": r.duty_cycle_hours, "readiness_score": r.readiness_score, "carbon_saved_kg": r.carbon_saved_kg} for r in records]

@app.get("/api/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_ev = db.query(EVTelemetry).count()
    anomalies_ev = db.query(EVTelemetry).filter(EVTelemetry.is_anomaly == True).count()
    total_harness = db.query(IndustrialReport).filter(IndustrialReport.check_type == "wire_harness").count()
    failed_harness = db.query(IndustrialReport).filter(IndustrialReport.check_type == "wire_harness", IndustrialReport.status == "Fail").count()
    pass_rate = 100.0
    if total_harness > 0:
        pass_rate = round(((total_harness - failed_harness) / total_harness) * 100, 2)
    last_weld = db.query(IndustrialReport).filter(IndustrialReport.check_type == "weld_electrode").order_by(IndustrialReport.timestamp.desc()).first()
    weld_health = float(last_weld.electrode_health) if last_weld else 100.0
    weld_cycles = int(last_weld.cycle_count) if last_weld else 0
    sc_total = db.query(SupplyChainEvent).count()
    sc_high_risk = db.query(SupplyChainEvent).filter(SupplyChainEvent.risk_score == 1).count()
    fleet_total = db.query(FleetReadiness).count()
    carbon_records = db.query(FleetReadiness).all()
    total_carbon_saved = sum(r.carbon_saved_kg for r in carbon_records)
    
    return {
        "ev_total_pushed": total_ev, "ev_anomaly_count": anomalies_ev,
        "harness_inspected_count": total_harness, "harness_pass_rate": pass_rate,
        "weld_electrode_health": weld_health, "weld_total_cycles": weld_cycles,
        "supply_chain_events": sc_total, "supply_chain_high_risk": sc_high_risk,
        "fleet_vehicles_tracked": fleet_total, "total_carbon_saved_kg": round(total_carbon_saved, 2)
    }

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
