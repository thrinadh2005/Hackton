import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import joblib

os.makedirs("models", exist_ok=True)

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

def train_pytorch_model(X, y, model_name, is_classification=False, epochs=50):
    print(f"\n--- Training Deep Learning Model: {model_name} ---")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    X_train_t = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_t = torch.tensor(y_train.values if hasattr(y_train, 'values') else y_train, dtype=torch.float32).unsqueeze(1)
    
    dataset = TensorDataset(X_train_t, y_train_t)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    model = TabularMLP(input_dim=X.shape[1], is_classification=is_classification)
    criterion = nn.BCELoss() if is_classification else nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    for epoch in range(epochs):
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            preds = model(batch_X)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            
    # Evaluation
    model.eval()
    with torch.no_grad():
        X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
        y_pred_t = model(X_test_t)
        
        if is_classification:
            y_pred = (y_pred_t.numpy() > 0.5).astype(int).flatten()
            acc = accuracy_score(y_test, y_pred)
            print(f"Accuracy: {acc:.4f}")
        else:
            y_pred = y_pred_t.numpy().flatten()
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            print(f"MSE: {mse:.3f} | R2 Score: {r2:.4f}")
            
    # Save
    joblib.dump(scaler, f"models/{model_name}_scaler.pkl")
    torch.save(model.state_dict(), f"models/{model_name}.pth")
    print(f"Saved {model_name} (PyTorch weights + Scaler)")

def train_ev_soh_model():
    np.random.seed(42)
    n_samples = 5000
    voltage = np.random.uniform(3.0, 4.2, n_samples)
    current = np.random.uniform(0.5, 3.0, n_samples)
    temp = np.random.uniform(20.0, 55.0, n_samples)
    cycles = np.random.randint(1, 1500, n_samples)
    
    soh = 100.0 - (cycles * 0.02) - (temp * 0.1) - (current * 0.5) - ((temp > 45) * 5.0)
    soh += np.random.normal(0, 0.5, n_samples)
    soh = np.clip(soh, 10.0, 100.0)
    
    X = pd.DataFrame({'voltage': voltage, 'current': current, 'temperature': temp, 'cycles': cycles})
    train_pytorch_model(X, soh, "ev_soh_model", is_classification=False)

def train_ev_motor_anomaly_model():
    print("\n--- Training Deep Autoencoder for Motor Anomaly ---")
    np.random.seed(42)
    n_samples = 4000
    normal_vibration = np.random.normal(0, 1.0, (n_samples, 3))
    
    scaler = StandardScaler()
    normal_scaled = scaler.fit_transform(normal_vibration)
    X_t = torch.tensor(normal_scaled, dtype=torch.float32)
    
    dataset = TensorDataset(X_t, X_t)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    model = AnomalyAutoencoder(input_dim=3)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    for epoch in range(40):
        for batch_X, _ in loader:
            optimizer.zero_grad()
            reconstructed = model(batch_X)
            loss = criterion(reconstructed, batch_X)
            loss.backward()
            optimizer.step()
            
    # Calculate threshold (95th percentile of reconstruction error on normal data)
    model.eval()
    with torch.no_grad():
        reconstructed_all = model(X_t)
        mse_errors = torch.mean((X_t - reconstructed_all)**2, dim=1).numpy()
        threshold = np.percentile(mse_errors, 95)
        print(f"Calculated Anomaly Threshold: {threshold:.4f}")
        
    joblib.dump(scaler, "models/ev_motor_anomaly_scaler.pkl")
    # Save threshold along with weights in a dict
    torch.save({'state_dict': model.state_dict(), 'threshold': threshold}, "models/ev_motor_anomaly_model.pth")
    print("Saved Motor Anomaly Autoencoder.")

def train_industrial_click_model():
    np.random.seed(42)
    n_samples = 4000
    freq = np.random.uniform(500.0, 4500.0, n_samples)
    db = np.random.uniform(40.0, 85.0, n_samples)
    duration = np.random.uniform(5.0, 60.0, n_samples)
    
    label = np.where((freq >= 2300) & (freq <= 3700) & (db >= 65) & (duration >= 12) & (duration <= 38), 1, 0)
    flip_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    label[flip_indices] = 1 - label[flip_indices]
    
    X = pd.DataFrame({'frequency_peak': freq, 'decibels': db, 'duration_ms': duration})
    train_pytorch_model(X, label, "industrial_click_model", is_classification=True)

def train_weld_electrode_health_model():
    np.random.seed(42)
    n_samples = 5000
    cycles = np.random.randint(1, 5000, n_samples)
    current = np.random.uniform(8.0, 15.0, n_samples)
    spatter = (cycles * 0.005) + (current * 0.2) + np.random.normal(0, 1.0, n_samples)
    spatter = np.clip(spatter, 0.0, 50.0)
    
    health = 100.0 - (cycles * 0.018) - (spatter * 0.3)
    health = np.clip(health, 0.0, 100.0)
    
    X = pd.DataFrame({'cycle_count': cycles, 'weld_current_ka': current, 'spatter_level': spatter})
    train_pytorch_model(X, health, "weld_electrode_health_model", is_classification=False)

def train_supply_chain_risk_model():
    np.random.seed(42)
    n_samples = 5000
    geo_risk = np.random.uniform(1.0, 10.0, n_samples)
    scarcity = np.random.uniform(1.0, 10.0, n_samples)
    defect_rate = np.random.uniform(0.1, 5.0, n_samples)
    lead_time = np.random.uniform(10.0, 90.0, n_samples)
    
    risk_score = (geo_risk * 0.3) + (scarcity * 0.4) + (defect_rate * 0.2) + (lead_time * 0.05)
    risk_score += (scarcity > 7.0) * (defect_rate > 3.0) * 3.0
    label = np.where(risk_score > 6.5, 1, 0)
    
    flip_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    label[flip_indices] = 1 - label[flip_indices]
    
    X = pd.DataFrame({'geopolitical_risk_score': geo_risk, 'material_scarcity_index': scarcity, 'supplier_defect_rate': defect_rate, 'lead_time_days': lead_time})
    train_pytorch_model(X, label, "supply_chain_risk_model", is_classification=True)

def train_fleet_readiness_model():
    np.random.seed(42)
    n_samples = 5000
    distance = np.random.uniform(20.0, 400.0, n_samples)
    payload = np.random.uniform(1.0, 40.0, n_samples)
    duty_cycle = np.random.uniform(4.0, 20.0, n_samples)
    
    score = 100.0 - (distance * 0.15) - (payload * 0.5) - (duty_cycle * 1.5)
    score -= (distance > 250) * (payload > 20) * 10.0
    score += np.random.normal(0, 3.0, n_samples)
    score = np.clip(score, 0.0, 100.0)
    
    X = pd.DataFrame({'route_distance_km': distance, 'payload_tons': payload, 'duty_cycle_hours': duty_cycle})
    train_pytorch_model(X, score, "fleet_readiness_model", is_classification=False)

if __name__ == "__main__":
    train_ev_soh_model()
    train_ev_motor_anomaly_model()
    train_industrial_click_model()
    train_weld_electrode_health_model()
    train_supply_chain_risk_model()
    train_fleet_readiness_model()
    print("\n--- ALL DEEP LEARNING MODELS SUCCESSFULLY TRAINED AND SERIALIZED ---")
