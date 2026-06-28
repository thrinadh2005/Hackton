import time
import random
import requests

API_URL = "http://localhost:8000"

def run_simulator():
    print("EdgeIntel-AM Telemetry Simulator Started.")
    print(f"Connecting to FastAPI backend at {API_URL}...")
    
    # Track cycle counters
    ev_cycles = 150
    weld_cycles = 2100
    
    # Loop indefinitely
    while True:
        try:
            # 1. Fetch current fault states from API
            resp = requests.get(f"{API_URL}/api/fault/states")
            faults = resp.json() if resp.status_code == 200 else {
                "battery_fault": False,
                "motor_fault": False,
                "harness_fault": False,
                "electrode_fault": False
            }
        except Exception:
            # Backend might not be up yet; wait and retry
            time.sleep(2)
            continue
            
        # ----------------------------------------------------
        # EV TELEMETRY SIMULATION
        # ----------------------------------------------------
        ev_cycles += 1
        
        # Base normal values
        voltage = round(random.uniform(3.7, 4.1), 3)
        current = round(random.uniform(1.2, 2.0), 3)
        temp = round(random.uniform(25.0, 32.0), 2)
        vib_x = round(random.normalvariate(0, 0.5), 3)
        vib_y = round(random.normalvariate(0, 0.5), 3)
        vib_z = round(random.normalvariate(0, 0.5), 3)
        fault_type = "Normal"
        
        # Inject faults if triggered
        if faults.get("battery_fault"):
            temp = round(random.uniform(55.0, 68.0), 2)  # High thermal surge
            voltage = round(random.uniform(3.1, 3.4), 3) # Cell voltage sag
            current = round(random.uniform(3.5, 5.0), 3) # Overcurrent
            fault_type = "Battery Thermal Runaway Warning"
            
        if faults.get("motor_fault"):
            # Heavy motor imbalance / bearing wear
            vib_x = round(random.normalvariate(2.5, 1.5), 3)
            vib_y = round(random.normalvariate(-2.0, 1.2), 3)
            vib_z = round(random.normalvariate(3.0, 2.0), 3)
            if fault_type == "Normal":
                fault_type = "Motor Bearing Anomaly"
            else:
                fault_type += " + Bearing Anomaly"

        ev_payload = {
            "voltage": voltage,
            "current": current,
            "temperature": temp,
            "cycles": ev_cycles,
            "vibration_x": vib_x,
            "vibration_y": vib_y,
            "vibration_z": vib_z,
            "fault_type": fault_type
        }
        
        try:
            requests.post(f"{API_URL}/api/telemetry/ev", json=ev_payload)
        except Exception as e:
            print(f"Error sending EV telemetry: {e}")

        # ----------------------------------------------------
        # INDUSTRIAL QUALITY CHECK SIMULATION
        # ----------------------------------------------------
        # Wire harness clicks checks happen every 3 iterations
        if ev_cycles % 3 == 0:
            harness_fault = faults.get("harness_fault")
            
            if harness_fault:
                # Click fails (loose seating)
                freq = round(random.uniform(800.0, 1800.0), 2) # Freq is too low
                db_level = round(random.uniform(45.0, 58.0), 2) # Sound is too quiet
                duration = round(random.uniform(5.0, 10.0), 2)  # Micro-click, incomplete
                camera_conf = round(random.uniform(0.60, 0.81), 2) # Misaligned visually
            else:
                # Perfect snap seating
                freq = round(random.uniform(2800.0, 3400.0), 2)
                db_level = round(random.uniform(68.0, 78.0), 2)
                duration = round(random.uniform(18.0, 28.0), 2)
                camera_conf = round(random.uniform(0.95, 0.99), 2)
                
            harness_payload = {
                "check_type": "wire_harness",
                "connector_type": random.choice(["TATA-C100", "TATA-C120", "EV-CONN-A"]),
                "camera_confidence": camera_conf,
                "click_acoustic_peak": freq,
                "decibels": db_level,
                "click_duration_ms": duration
            }
            
            try:
                requests.post(f"{API_URL}/api/telemetry/industrial", json=harness_payload)
            except Exception as e:
                print(f"Error sending Harness telemetry: {e}")
                
        # Weld electrode inspections happen every 4 iterations
        if ev_cycles % 4 == 0:
            weld_cycles += 5
            electrode_fault = faults.get("electrode_fault")
            
            # Normal wear accumulation
            base_spatter = (weld_cycles * 0.004) + random.uniform(1.0, 3.0)
            weld_curr = round(random.uniform(11.0, 12.5), 2)
            
            if electrode_fault:
                # Extreme pitting and wear
                weld_cycles += 200 # artificially age electrode
                base_spatter = round(random.uniform(32.0, 48.0), 2) # spatter spikes
                weld_curr = round(random.uniform(8.5, 9.8), 2)       # current drop
                
            weld_payload = {
                "check_type": "weld_electrode",
                "cycle_count": weld_cycles,
                "weld_current_ka": weld_curr,
                "spatter_level": round(base_spatter, 2)
            }
            
            try:
                requests.post(f"{API_URL}/api/telemetry/industrial", json=weld_payload)
            except Exception as e:
                print(f"Error sending Weld telemetry: {e}")
                
        # ----------------------------------------------------
        # SUPPLY CHAIN SIMULATION (every 5 iterations)
        # ----------------------------------------------------
        if ev_cycles % 5 == 0:
            sc_fault = faults.get("supply_chain_fault")
            
            geo = round(random.uniform(1.0, 4.0), 2)
            scarcity = round(random.uniform(1.0, 4.0), 2)
            defect = round(random.uniform(0.1, 1.5), 2)
            lead = round(random.uniform(10.0, 30.0), 2)
            
            if sc_fault:
                geo = round(random.uniform(7.0, 10.0), 2)
                scarcity = round(random.uniform(8.0, 10.0), 2)
                defect = round(random.uniform(3.0, 5.0), 2)
                lead = round(random.uniform(45.0, 90.0), 2)
                
            sc_payload = {
                "supplier_id": random.choice(["SUP-LITHIUM-A", "SUP-COBALT-B", "SUP-NICKEL-C"]),
                "material": random.choice(["Lithium", "Cobalt", "Nickel", "NMC Cell"]),
                "geopolitical_risk_score": geo,
                "material_scarcity_index": scarcity,
                "supplier_defect_rate": defect,
                "lead_time_days": lead
            }
            try:
                requests.post(f"{API_URL}/api/telemetry/supply_chain", json=sc_payload)
            except Exception as e:
                print(f"Error sending Supply Chain telemetry: {e}")

        # ----------------------------------------------------
        # FLEET READINESS SIMULATION (every 6 iterations)
        # ----------------------------------------------------
        if ev_cycles % 6 == 0:
            fleet_fault = faults.get("fleet_fault")
            
            dist = round(random.uniform(50.0, 150.0), 2)
            payload_t = round(random.uniform(2.0, 10.0), 2)
            duty = round(random.uniform(4.0, 10.0), 2)
            
            if fleet_fault:
                # Sub-optimal for EV replacement
                dist = round(random.uniform(300.0, 500.0), 2)
                payload_t = round(random.uniform(25.0, 40.0), 2)
                duty = round(random.uniform(16.0, 24.0), 2)
            
            # Simulated calculation of Carbon (diesel emissions avoided vs EV)
            # Diesel: ~2.68 kg CO2 per liter, truck maybe 3 km/L -> ~0.9 kg/km
            carbon_saved = dist * 0.9
            
            fleet_payload = {
                "vehicle_id": f"FLEET-TRK-{random.randint(100, 999)}",
                "route_distance_km": dist,
                "payload_tons": payload_t,
                "duty_cycle_hours": duty,
                "carbon_saved_kg": carbon_saved
            }
            try:
                requests.post(f"{API_URL}/api/telemetry/fleet", json=fleet_payload)
            except Exception as e:
                print(f"Error sending Fleet telemetry: {e}")
                
        time.sleep(1)

if __name__ == "__main__":
    run_simulator()
