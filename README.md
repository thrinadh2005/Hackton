# AI for Industrial EV Supply Chain & Asset Intelligence: Accelerating Net Zero

**A comprehensive, Agentic AI platform built for the Net Zero Hackathon.** 
This project directly addresses the industrial EV transition bottleneck by providing a unified AI layer that handles both operational asset performance (APM) and critical supply chain visibility.

## Hackathon Problem Statement Alignment

This platform implements all core themes required by the prompt using a combination of **Deep Learning (PyTorch)** and **Generative AI (Transformers)**:

1. **EV Asset Performance Management (APM) Agent**
   - *Requirement:* Monitor battery state-of-health, thermal events, generate predictive maintenance triggers.
   - *Implementation:* PyTorch `TabularMLP` predicts Battery SOH degradation. A PyTorch `Deep Autoencoder` constantly analyzes motor vibrations (X, Y, Z) to detect mechanical anomalies in real-time.

2. **Fleet Electrification Readiness & Procurement Intelligence**
   - *Requirement:* Analyze route, payload, duty cycles to generate a transition readiness index.
   - *Implementation:* Deep Learning regressor ingests fleet telemetry and outputs a 0-100 `Readiness Score`, helping organizations prioritize which heavy vehicles to replace with EVs first.

3. **EV Supply Chain Risk & Traceability Agent**
   - *Requirement:* Track critical battery materials (Lithium, Cobalt), flag geopolitical exposure and supplier risk.
   - *Implementation:* Evaluates global supplier nodes based on geopolitical scores, material scarcity, defect rates, and lead times. A **Gen AI (LLM) Agent** interprets supply chain shocks and broadcasts real-time mitigation strategies.

4. **Manufacturing Quality Intelligence (QMS Integration)**
   - *Requirement:* Detect quality drift before defective product reaches assembly.
   - *Implementation:* Includes models for **Wire Harness Acoustic Profiling** (detecting seating faults via sound wave analysis) and **Weld Electrode Health Tracking** (predicting wear based on current and spatter).

5. **Net Zero Progress & Carbon Intelligence Tracker**
   - *Requirement:* Track fleet electrification progress and quantify Scope 1 and Scope 3 emission reductions.
   - *Implementation:* Live carbon offset tracking is integrated into the React Dashboard's top KPI bar.

## Expected Deliverables Included
- ✅ **Working Prototype:** A fully functional FastAPI Backend (with real PyTorch tensors) and an interactive React.js Frontend Dashboard.
- ✅ **Architecture Diagram:** A dynamic, programmatic 3D architecture visualization built in Blender Python (`blender_visualization.py`).
- *(Add your Presentation Deck and Demo Video to the repository before submitting!)*

## Tech Stack
- **AI/ML Layer:** PyTorch, HuggingFace Transformers (GenAI), Scikit-Learn (Scaling/Metrics)
- **Backend Edge Gateway:** FastAPI, Uvicorn, WebSockets, SQLAlchemy (SQLite)
- **Frontend Dashboard:** React, Vite, Recharts, Lucide Icons, Vanilla CSS
- **3D Visualization:** Blender Python API (`bpy`)

## Getting Started
To run the prototype locally:
```powershell
./start.bat
```
Navigate to `http://localhost:5173` to interact with the AI Fault Control Room!
