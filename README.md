# EdgeIntel-AM: AI for Industrial EV Supply Chain & Asset Intelligence

![NetZero Platform Banner](https://img.shields.io/badge/NetZero-Accelerating%20Electrification-brightgreen?style=for-the-badge)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)

A comprehensive, **Agentic AI platform** built for the Net Zero Hackathon. This project directly addresses the industrial EV transition bottleneck by providing a unified AI layer that handles both operational asset performance (APM) and critical supply chain visibility.

---

## 📖 Table of Contents
1. [Project Overview](#project-overview)
2. [Hackathon Problem Statement Alignment](#hackathon-problem-statement-alignment)
3. [System Architecture](#system-architecture)
4. [Deep Learning & GenAI Models](#deep-learning--genai-models)
5. [Getting Started (Installation)](#getting-started-installation)
6. [User Guide: How to Demo the Project](#user-guide-how-to-demo-the-project)
7. [Expected Deliverables](#expected-deliverables)

---

## 🌟 Project Overview
As the world transitions to electric vehicles (EVs) in industrial and commercial sectors, operators face two major hurdles: managing the predictive maintenance of complex battery and motor systems, and navigating a highly volatile, geopolitical supply chain for critical minerals (Lithium, Cobalt, etc.).

**EdgeIntel-AM** solves this by fusing **Deep Learning (PyTorch)** with **Generative AI (HuggingFace Transformers)**. It ingests high-frequency telemetry from fleets, factory floors, and supply chain nodes, utilizing real-time neural networks to predict anomalies and a GenAI Agent to instantly generate human-readable mitigation strategies.

---

## 🎯 Hackathon Problem Statement Alignment

This platform implements all 5 core themes required by the hackathon prompt:

### 1. EV Asset Performance Management (APM) Agent
*   **Requirement:** Monitor battery state-of-health, thermal events, generate predictive maintenance triggers.
*   **Implementation:** A PyTorch `TabularMLP` predicts Battery SOH degradation based on voltage, current, and temperature. A PyTorch `Deep Autoencoder` constantly analyzes 3-axis motor vibrations to detect mechanical anomalies in real-time.

### 2. Fleet Electrification Readiness & Procurement Intelligence
*   **Requirement:** Analyze route, payload, and duty cycles to generate a transition readiness index.
*   **Implementation:** A Deep Learning regressor ingests fleet telemetry and outputs a 0-100 `Readiness Score`, helping organizations prioritize which heavy-duty diesel vehicles to replace with EVs first to maximize ROI and carbon reduction.

### 3. EV Supply Chain Risk & Traceability Agent
*   **Requirement:** Track critical battery materials, flag geopolitical exposure and supplier risk.
*   **Implementation:** Evaluates global supplier nodes based on geopolitical scores, material scarcity, defect rates, and lead times. A **Gen AI (LLM) Agent** interprets these supply chain shocks and broadcasts real-time mitigation strategies to the dashboard.

### 4. Manufacturing Quality Intelligence (QMS Integration)
*   **Requirement:** Detect quality drift before defective product reaches assembly.
*   **Implementation:** 
    *   **Wire Harness Acoustic Profiling:** AI evaluates connector seating via acoustic frequency and vision confidence.
    *   **Weld Electrode Health Tracking:** Predicts remaining electrode life based on welding current and spatter index, stopping production before bad welds occur.

### 5. Net Zero Progress & Carbon Intelligence Tracker
*   **Requirement:** Track fleet electrification progress and quantify Scope 1 and Scope 3 emission reductions.
*   **Implementation:** Live carbon offset tracking (diesel emissions avoided) is integrated directly into the React Dashboard's top KPI bar.

---

## ⚙️ System Architecture

The project consists of 4 main components working in unison:
1.  **Telemetry Simulator (`backend/simulator.py`):** Generates synthetic, high-frequency IoT data for EVs, factory equipment, and supply chains.
2.  **FastAPI Edge Gateway (`backend/main.py`):** The central hub. It receives telemetry, standardizes it, and feeds it into the AI models.
3.  **PyTorch & GenAI Engine (`backend/train_models.py`):** Hosts the deep neural networks and the HuggingFace `distilgpt2` NLP pipeline.
4.  **React.js Dashboard (`frontend/src/App.jsx`):** A glassmorphism-styled, real-time command center receiving data via WebSockets.

---

## 🧠 Deep Learning & GenAI Models

Our backend utilizes 6 distinct PyTorch models trained on high-variance synthetic datasets:
*   **ev_soh_model.pth:** Multi-layer Perceptron (Regression).
*   **ev_motor_anomaly_model.pth:** Deep Autoencoder (Unsupervised Anomaly Detection using MSE reconstruction loss).
*   **industrial_click_model.pth:** Classification MLP for QA acoustic passing.
*   **weld_electrode_health_model.pth:** Regression MLP tracking tool wear.
*   **supply_chain_risk_model.pth:** Classification MLP identifying supplier failure probabilities.
*   **fleet_readiness_model.pth:** Regression MLP scoring transition viability.

**Generative AI (`distilgpt2`):** Loaded via HuggingFace's `pipeline`. When a PyTorch model flags an anomaly (e.g., Motor Vibration > 1.2 MSE), the exact context is passed to the LLM, which generates a prescriptive action in real-time.

---

## 🚀 Getting Started (Installation)

### Prerequisites
*   Python 3.9+
*   Node.js v16+
*   Git

### 1-Click Launch (Windows)
We have provided a convenient batch script that handles the entire setup (creating virtual environments, installing dependencies, pre-training the AI models, and launching all servers).

1. Clone the repository:
   ```bash
   git clone https://github.com/thrinadh2005/Hackton.git
   cd Hackton
   ```
2. Run the startup script:
   ```powershell
   ./start.bat
   ```
3. The script will open three terminal windows (Backend, Simulator, Frontend). *Note: The very first run will take a few minutes as it downloads PyTorch and the HuggingFace AI weights (~500MB).*
4. Your browser will automatically open to `http://localhost:5173`.

---

## 🎮 User Guide: How to Demo the Project

Once the dashboard is running, follow these steps to demonstrate the AI capabilities to the judges:

### 1. Observe the Baseline
Navigate through the tabs (**EV Asset Performance**, **Supply Chain Risk**, **QMS Manufacturing**, **Fleet Electrification**). Notice how the live charts are plotting standard, healthy data being fed from the telemetry simulator.

### 2. Open the "AI Fault Control Room"
Click the **🎛️ AI Fault Control Room** tab. This panel allows you to artificially inject realistic physical and geopolitical faults into the simulation data stream.

### 3. Inject a Supply Chain Shock
1. Click the **"INJECT FAULT"** button under the **Supply Chain Shock** card.
2. Quickly navigate back to the **🌍 Supply Chain Risk** tab.
3. You will see the Geopolitical Risk bar chart spike drastically. The AI will classify the material shipment as **"High Risk"**.
4. **Look at the Gen AI Feed:** Right below the top KPIs, you will see the GenAI agent output a live message (e.g., *"Supply Chain Shock Detected. Pivot to tier-2 domestic supplier..."*).

### 4. Trigger Predictive Maintenance (APM)
1. Go back to the Control Room and inject a **Motor Bearing Outlier**.
2. Navigate to the **🚗 EV Asset Performance** tab.
3. The PyTorch Autoencoder will fail to reconstruct the erratic vibration data, causing the MSE Anomaly Score to exceed the safety threshold. 
4. A red, shaking alert banner will appear, and the GenAI feed will advise on immediate maintenance protocols.

---

## 📦 Expected Deliverables
- [x] **Working Prototype:** Fully functional FastAPI Backend, PyTorch Inference engine, and React.js WebSocket Frontend.
- [x] **Architecture Diagram:** An animated, programmatic 3D visualization using Blender Python (`blender_visualization.py`).
- [ ] **Presentation Deck:** *(Link to be added)*
- [ ] **Demo Video:** *(Link to be added)*

---
*Built for the Net Zero Hackathon.*
