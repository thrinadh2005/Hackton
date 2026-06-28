import React, { useState, useEffect } from 'react';
import { 
  Activity, Zap, Cpu, AlertTriangle, ShieldCheck, Gauge, Thermometer, 
  TrendingDown, Volume2, Eye, Sliders, RefreshCw, Flame, Wrench,
  Globe, Package, Truck, Leaf, MapPin, BarChart3, AlertOctagon, TrendingUp
} from 'lucide-react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, Legend
} from 'recharts';

export default function App() {
  const [activeTab, setActiveTab] = useState('apm');
  const [faultStates, setFaultStates] = useState({
    battery_fault: false,
    motor_fault: false,
    harness_fault: false,
    electrode_fault: false,
    supply_chain_fault: false,
    fleet_fault: false
  });
  
  // State for live stream
  const [evHistory, setEvHistory] = useState([]);
  const [industrialHistory, setIndustrialHistory] = useState([]);
  const [supplyChainHistory, setSupplyChainHistory] = useState([]);
  const [fleetHistory, setFleetHistory] = useState([]);
  const [genAiInsights, setGenAiInsights] = useState([]);
  const [kpis, setKpis] = useState({
    ev_total_pushed: 0,
    ev_anomaly_count: 0,
    harness_inspected_count: 0,
    harness_pass_rate: 100,
    weld_electrode_health: 100,
    weld_total_cycles: 0,
    supply_chain_events: 0,
    supply_chain_high_risk: 0,
    fleet_vehicles_tracked: 0,
    total_carbon_saved_kg: 0
  });

  // REST fetch for initial state
  const fetchData = async () => {
    try {
      const statsRes = await fetch('/api/stats');
      if (statsRes.ok) setKpis(await statsRes.json());
      
      const evRes = await fetch('/api/history/ev?limit=30');
      if (evRes.ok) setEvHistory((await evRes.json()).reverse());

      const indRes = await fetch('/api/history/industrial?limit=30');
      if (indRes.ok) setIndustrialHistory((await indRes.json()).reverse());

      const scRes = await fetch('/api/history/supply_chain?limit=30');
      if (scRes.ok) setSupplyChainHistory((await scRes.json()).reverse());

      const flRes = await fetch('/api/history/fleet?limit=30');
      if (flRes.ok) setFleetHistory((await flRes.json()).reverse());

      const faultRes = await fetch('/api/fault/states');
      if (faultRes.ok) setFaultStates(await faultRes.json());
    } catch (err) {
      console.error("Error fetching initial API data:", err);
    }
  };

  // Setup WebSocket connection
  useEffect(() => {
    fetchData();
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live`;
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'ev') {
        setEvHistory(prev => [...prev, message.data].slice(-30));
      } else if (message.type === 'industrial') {
        setIndustrialHistory(prev => [...prev, message.data].slice(-30));
      } else if (message.type === 'supply_chain') {
        setSupplyChainHistory(prev => [...prev, message.data].slice(-30));
      } else if (message.type === 'fleet') {
        setFleetHistory(prev => [...prev, message.data].slice(-30));
      } else if (message.type === 'genai_insight') {
        setGenAiInsights(prev => [...prev, message.data].slice(-5));
      }
      
      fetch('/api/stats').then(res => res.json()).then(stats => setKpis(stats)).catch(err => console.error(err));
    };

    socket.onerror = (err) => console.error("WebSocket encountered error:", err);
    return () => socket.close();
  }, []);

  const toggleFault = async (faultKey) => {
    const nextState = !faultStates[faultKey];
    try {
      const res = await fetch('/api/fault/inject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [faultKey]: nextState })
      });
      if (res.ok) setFaultStates(prev => ({ ...prev, [faultKey]: nextState }));
    } catch (err) {
      console.error("Failed to inject fault:", err);
    }
  };

  const latestEv = evHistory[evHistory.length - 1] || { voltage: 3.8, current: 1.5, temperature: 28, predicted_soh: 98, is_anomaly: false, fault_type: "Normal", anomaly_score: 1.0 };
  const latestHarness = industrialHistory.filter(h => h.check_type === 'wire_harness').slice(-1)[0] || { connector_type: "TATA-C100", camera_confidence: 0.98, click_status: "PASS", status: "Normal", click_acoustic_peak: 3100 };
  const latestWeld = industrialHistory.filter(w => w.check_type === 'weld_electrode').slice(-1)[0] || { cycle_count: 0, spatter_level: 0, electrode_health: 100 };
  const latestSC = supplyChainHistory[supplyChainHistory.length - 1] || { material: "N/A", geopolitical_risk_score: 0, supplier_defect_rate: 0, status: "Stable", risk_score: 0 };
  const latestFleet = fleetHistory[fleetHistory.length - 1] || { route_distance_km: 0, payload_tons: 0, readiness_score: 100, vehicle_id: "N/A" };

  return (
    <div className="app-container">
      {/* Header Panel */}
      <header className="glass-panel header-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Leaf className="pulse-glow-green" style={{ color: 'var(--neon-green)', width: '32px', height: '32px' }} />
          <div>
            <h1 className="title-glow" style={{ fontSize: '1.75rem', color: '#fff' }}>NetZero AI</h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--neon-cyan)' }}>Industrial EV Supply Chain & Asset Intelligence</p>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--neon-green)', display: 'inline-block' }} className="pulse-glow-green"></span>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--neon-green)' }}>AI MODELS ONLINE</span>
          </div>
          <button className="btn-secondary" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }} onClick={fetchData}>
            <RefreshCw style={{ width: '14px', height: '14px' }} /> Sync
          </button>
        </div>
      </header>

      {/* KPI Cards Strip */}
      <section className="kpi-grid">
        <div className="glass-panel glass-card" style={{ borderLeft: '3px solid var(--neon-green)' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>CARBON EMISSIONS AVOIDED</p>
          <h3 style={{ fontSize: '1.8rem', fontFamily: 'var(--font-display)', margin: '0.35rem 0', color: 'var(--neon-green)' }}>{kpis.total_carbon_saved_kg} kg</h3>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Scope 1 & 3 Offset Tracking</p>
        </div>
        <div className="glass-panel glass-card" style={{ borderLeft: `3px solid ${kpis.supply_chain_high_risk > 0 ? 'var(--neon-red)' : 'var(--neon-cyan)'}` }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>SUPPLIER RISK EVENTS</p>
          <h3 style={{ fontSize: '1.8rem', fontFamily: 'var(--font-display)', margin: '0.35rem 0' }} className={kpis.supply_chain_high_risk > 0 ? 'pulse-glow-red' : ''}>
            {kpis.supply_chain_high_risk} <span style={{fontSize: '1rem', color: 'var(--text-muted)'}}>/ {kpis.supply_chain_events}</span>
          </h3>
          <p style={{ fontSize: '0.7rem', color: kpis.supply_chain_high_risk > 0 ? 'var(--neon-red)' : 'var(--neon-green)' }}>
            {kpis.supply_chain_high_risk > 0 ? 'Active Supply Chain Shock' : 'Supply Chain Stable'}
          </p>
        </div>
        <div className="glass-panel glass-card" style={{ borderLeft: `3px solid ${kpis.ev_anomaly_count > 0 ? 'var(--neon-orange)' : 'var(--neon-cyan)'}` }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>FLEET APM ANOMALIES</p>
          <h3 style={{ fontSize: '1.8rem', fontFamily: 'var(--font-display)', margin: '0.35rem 0' }}>{kpis.ev_anomaly_count}</h3>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Live Motor & Battery Diagnostics</p>
        </div>
        <div className="glass-panel glass-card" style={{ borderLeft: `3px solid ${kpis.harness_pass_rate < 90 ? 'var(--neon-red)' : 'var(--neon-cyan)'}` }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>MANUFACTURING YIELD</p>
          <h3 style={{ fontSize: '1.8rem', fontFamily: 'var(--font-display)', margin: '0.35rem 0' }}>{kpis.harness_pass_rate}%</h3>
          <p style={{ fontSize: '0.7rem', color: kpis.harness_pass_rate < 90 ? 'var(--neon-orange)' : 'var(--neon-green)' }}>
            Component Assembly QMS
          </p>
        </div>
      </section>

      {/* Gen AI Insights Feed */}
      {genAiInsights.length > 0 && (
        <section className="glass-panel" style={{ padding: '1rem', marginBottom: '1.5rem', background: 'rgba(0,0,0,0.4)', borderLeft: '4px solid var(--neon-orange)' }}>
          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap style={{ color: 'var(--neon-orange)', width: '16px', height: '16px' }} /> Gen AI Real-Time Insights
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '120px', overflowY: 'auto' }}>
            {genAiInsights.slice().reverse().map((insight, idx) => (
              <div key={idx} style={{ padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', fontSize: '0.85rem', animation: 'fadeIn 0.5s ease-out' }}>
                <span style={{ color: 'var(--neon-cyan)', fontWeight: 'bold', marginRight: '0.5rem' }}>[{insight.context}]</span>
                <span style={{ color: '#fff' }}>{insight.insight}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Main Tab Controller & Panel Grid */}
      <main className="glass-panel" style={{ padding: '1.5rem', minHeight: '600px' }}>
        <div className="tabs-container">
          <button className={`tab-btn ${activeTab === 'apm' ? 'active' : ''}`} onClick={() => setActiveTab('apm')}>
            🚗 EV Asset Performance
          </button>
          <button className={`tab-btn ${activeTab === 'sc' ? 'active' : ''}`} onClick={() => setActiveTab('sc')}>
            🌍 Supply Chain Risk
          </button>
          <button className={`tab-btn ${activeTab === 'qms' ? 'active' : ''}`} onClick={() => setActiveTab('qms')}>
            🏭 QMS Manufacturing
          </button>
          <button className={`tab-btn ${activeTab === 'fleet' ? 'active' : ''}`} onClick={() => setActiveTab('fleet')}>
            🚛 Fleet Electrification & NetZero
          </button>
          <button className={`tab-btn ${activeTab === 'control_room' ? 'active' : ''}`} onClick={() => setActiveTab('control_room')}>
            🎛️ AI Fault Control Room
          </button>
        </div>

        {/* TAB 1: EV APM VIEW */}
        {activeTab === 'apm' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <h2 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
                Predictive Maintenance (APM)
              </h2>
              {latestEv.fault_type !== "Normal" && (
                <div className={`alert-banner ${latestEv.is_anomaly ? 'alert-error' : 'alert-warning'} ${latestEv.is_anomaly ? 'shaking' : ''}`}>
                  <AlertTriangle style={{ width: '20px', height: '20px' }} />
                  <div>
                    <strong>{latestEv.fault_type}</strong>
                    <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Anomaly Score: {latestEv.anomaly_score?.toFixed(3)}</div>
                  </div>
                </div>
              )}
              <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <Gauge style={{ color: 'var(--neon-cyan)' }} />
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Battery State of Health (SOH)</span>
                    <span style={{ fontWeight: 600, color: 'var(--neon-green)' }}>{latestEv.predicted_soh?.toFixed(1)}%</span>
                  </div>
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', marginTop: '0.35rem', overflow: 'hidden' }}>
                    <div style={{ height: '100%', background: 'var(--neon-green)', width: `${latestEv.predicted_soh}%` }}></div>
                  </div>
                </div>
              </div>
              <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <Thermometer style={{ color: latestEv.temperature > 50 ? 'var(--neon-red)' : 'var(--neon-cyan)' }} />
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Cell Thermal Monitor</span>
                  <h4 style={{ fontSize: '1.3rem', fontFamily: 'var(--font-display)', color: latestEv.temperature > 50 ? 'var(--neon-red)' : '#fff' }}>
                    {latestEv.temperature?.toFixed(2)} °C
                  </h4>
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div className="glass-card" style={{ height: '260px' }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <TrendingDown style={{ width: '16px', height: '16px' }} /> EV Battery SOH Degradation vs Cycles
                </h3>
                <ResponsiveContainer width="100%" height="90%">
                  <LineChart data={evHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                    <XAxis dataKey="cycles" stroke="var(--text-muted)" fontSize={11} />
                    <YAxis domain={[0, 100]} stroke="var(--text-muted)" fontSize={11} />
                    <Tooltip contentStyle={{ background: 'var(--bg-secondary)', borderColor: 'var(--border-glass)' }} />
                    <Line type="monotone" dataKey="predicted_soh" stroke="var(--neon-green)" strokeWidth={2} dot={false} name="AI SOH Prediction (%)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SUPPLY CHAIN RISK */}
        {activeTab === 'sc' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <h2 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Globe style={{ color: 'var(--neon-cyan)' }} /> Global EV Battery Material Supply Chain
            </h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
              <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Latest Material Shipment</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <Package style={{ color: 'var(--neon-orange)', width: '32px', height: '32px' }} />
                  <div>
                    <div style={{ fontWeight: 600 }}>{latestSC.material}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{latestSC.supplier_id}</div>
                  </div>
                </div>
                
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.8rem' }}>AI Risk Assessment</span>
                    <span style={{ fontWeight: 600, color: latestSC.risk_score === 1 ? 'var(--neon-red)' : 'var(--neon-green)' }}>
                      {latestSC.status}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    <span>Geo Risk: {latestSC.geopolitical_risk_score?.toFixed(1)}</span>
                    <span>Defect Rate: {latestSC.supplier_defect_rate?.toFixed(1)}%</span>
                  </div>
                </div>

                {latestSC.risk_score === 1 && (
                  <div className="alert-banner alert-error shaking" style={{ padding: '0.5rem' }}>
                    <AlertOctagon style={{ width: '16px', height: '16px' }} />
                    <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Supply Chain Shock Detected</span>
                  </div>
                )}
              </div>
              
              <div className="glass-card" style={{ height: '300px' }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <BarChart3 style={{ width: '16px', height: '16px' }} /> Geo-Political vs Defect Risk Matrix
                </h3>
                <ResponsiveContainer width="100%" height="90%">
                  <BarChart data={supplyChainHistory.slice(-15)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                    <XAxis dataKey="material" stroke="var(--text-muted)" fontSize={11} />
                    <YAxis stroke="var(--text-muted)" fontSize={11} />
                    <Tooltip contentStyle={{ background: 'var(--bg-secondary)', borderColor: 'var(--border-glass)' }} />
                    <Legend />
                    <Bar dataKey="geopolitical_risk_score" fill="var(--neon-orange)" name="Geopolitical Risk" />
                    <Bar dataKey="supplier_defect_rate" fill="var(--neon-cyan)" name="Defect Rate %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: QMS MANUFACTURING */}
        {activeTab === 'qms' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <h2 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldCheck style={{ color: 'var(--neon-cyan)' }} /> Component Traceability & QMS
              </h2>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                <div style={{ flex: 1, height: '120px', background: 'rgba(0,0,0,0.4)', border: `1px solid ${latestHarness.status === 'Normal' ? 'var(--neon-green)' : 'var(--neon-red)'}`, borderRadius: '8px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                  <Eye style={{ color: 'var(--text-muted)', width: '24px', height: '24px', marginBottom: '0.25rem' }} />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Assembly Alignment</span>
                  <span style={{ fontSize: '0.75rem', color: latestHarness.camera_confidence > 0.85 ? 'var(--neon-green)' : 'var(--neon-red)' }}>
                    Vision Conf: {(latestHarness.camera_confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ flex: 1, height: '120px', background: 'rgba(0,0,0,0.4)', border: `1px solid ${latestHarness.click_status === 'PASS' ? 'var(--neon-green)' : 'var(--neon-red)'}`, borderRadius: '8px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                  <Volume2 style={{ color: 'var(--text-muted)', width: '24px', height: '24px', marginBottom: '0.25rem' }} />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Acoustic Sign-off</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--neon-cyan)' }}>Peak: {latestHarness.click_acoustic_peak?.toFixed(0)} Hz</span>
                </div>
              </div>
            </div>

            <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <h2 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Flame style={{ color: 'var(--neon-orange)' }} /> Pack Welding Health Tracker
              </h2>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Electrode Health Remaining</span>
                <span style={{ fontWeight: 700, color: latestWeld.electrode_health < 30 ? 'var(--neon-red)' : 'var(--neon-cyan)' }}>
                  {latestWeld.electrode_health?.toFixed(1)}%
                </span>
              </div>
              <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', background: latestWeld.electrode_health < 30 ? 'var(--neon-red)' : 'linear-gradient(to right, var(--neon-cyan), var(--neon-green))', width: `${latestWeld.electrode_health}%` }}></div>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Weld Spatter Index: {latestWeld.spatter_level?.toFixed(2)}</p>
            </div>
          </div>
        )}

        {/* TAB 4: FLEET & NETZERO */}
        {activeTab === 'fleet' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <h2 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Truck style={{ color: 'var(--neon-cyan)' }} /> Fleet Electrification Readiness
              </h2>
              <div className="glass-card" style={{ background: 'rgba(0,0,0,0.2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <MapPin style={{ color: 'var(--text-secondary)' }} />
                  <span style={{ fontWeight: 600 }}>{latestFleet.vehicle_id}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                  <span>Duty Cycle (Hrs)</span>
                  <span style={{ color: 'var(--neon-cyan)' }}>{latestFleet.duty_cycle_hours?.toFixed(1)} h</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                  <span>Route Distance</span>
                  <span style={{ color: 'var(--neon-orange)' }}>{latestFleet.route_distance_km?.toFixed(1)} km</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', fontSize: '0.8rem' }}>
                  <span>Average Payload</span>
                  <span style={{ color: 'var(--text-secondary)' }}>{latestFleet.payload_tons?.toFixed(1)} Tons</span>
                </div>

                <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>AI EV Transition Readiness Score</span>
                  <div style={{ fontSize: '2rem', fontFamily: 'var(--font-display)', color: latestFleet.readiness_score > 60 ? 'var(--neon-green)' : 'var(--neon-red)' }}>
                    {latestFleet.readiness_score?.toFixed(0)} <span style={{fontSize: '1rem'}}>/ 100</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="glass-card" style={{ height: '380px' }}>
              <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Leaf style={{ width: '16px', height: '16px', color: 'var(--neon-green)' }} /> Scope 1 & 3 Carbon Emissions Avoided vs Readiness
              </h3>
              <ResponsiveContainer width="100%" height="90%">
                <AreaChart data={fleetHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                  <XAxis dataKey="vehicle_id" stroke="var(--text-muted)" fontSize={11} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} />
                  <Tooltip contentStyle={{ background: 'var(--bg-secondary)', borderColor: 'var(--border-glass)' }} />
                  <Area type="monotone" dataKey="readiness_score" stroke="var(--neon-cyan)" fill="var(--neon-cyan-glow)" name="EV Readiness" />
                  <Area type="monotone" dataKey="carbon_saved_kg" stroke="var(--neon-green)" fill="rgba(16,185,129,0.2)" name="Carbon Saved (kg)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* TAB 5: CONTROL ROOM */}
        {activeTab === 'control_room' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <h2 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sliders style={{ color: 'var(--neon-cyan)' }} /> NetZero Platform Simulation Controls
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
              
              <div className="glass-card" style={{ border: `1px solid ${faultStates.battery_fault ? 'var(--neon-red)' : 'var(--border-glass)'}` }}>
                <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.5rem' }}><Thermometer style={{ color: 'var(--neon-red)' }} /> Thermal Runaway</h3>
                <button className="btn-secondary" style={{ width: '100%', background: faultStates.battery_fault ? 'var(--neon-red)' : 'transparent', color: faultStates.battery_fault ? '#000' : '#fff' }} onClick={() => toggleFault('battery_fault')}>
                  {faultStates.battery_fault ? "FAULT ACTIVE" : "INJECT FAULT"}
                </button>
              </div>

              <div className="glass-card" style={{ border: `1px solid ${faultStates.motor_fault ? 'var(--neon-red)' : 'var(--border-glass)'}` }}>
                <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.5rem' }}><Activity style={{ color: 'var(--neon-cyan)' }} /> Motor Bearing Outlier</h3>
                <button className="btn-secondary" style={{ width: '100%', background: faultStates.motor_fault ? 'var(--neon-red)' : 'transparent', color: faultStates.motor_fault ? '#000' : '#fff' }} onClick={() => toggleFault('motor_fault')}>
                  {faultStates.motor_fault ? "FAULT ACTIVE" : "INJECT FAULT"}
                </button>
              </div>

              <div className="glass-card" style={{ border: `1px solid ${faultStates.supply_chain_fault ? 'var(--neon-red)' : 'var(--border-glass)'}` }}>
                <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.5rem' }}><Globe style={{ color: 'var(--neon-orange)' }} /> Supply Chain Shock</h3>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Spikes geopolitical risk and lead times for battery materials.</p>
                <button className="btn-secondary" style={{ width: '100%', background: faultStates.supply_chain_fault ? 'var(--neon-red)' : 'transparent', color: faultStates.supply_chain_fault ? '#000' : '#fff' }} onClick={() => toggleFault('supply_chain_fault')}>
                  {faultStates.supply_chain_fault ? "FAULT ACTIVE" : "INJECT FAULT"}
                </button>
              </div>

              <div className="glass-card" style={{ border: `1px solid ${faultStates.fleet_fault ? 'var(--neon-red)' : 'var(--border-glass)'}` }}>
                <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.5rem' }}><Truck style={{ color: 'var(--neon-orange)' }} /> Fleet Sub-Optimal Route</h3>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Pushes high payload/distance data, lowering EV transition readiness score.</p>
                <button className="btn-secondary" style={{ width: '100%', background: faultStates.fleet_fault ? 'var(--neon-red)' : 'transparent', color: faultStates.fleet_fault ? '#000' : '#fff' }} onClick={() => toggleFault('fleet_fault')}>
                  {faultStates.fleet_fault ? "FAULT ACTIVE" : "INJECT FAULT"}
                </button>
              </div>
              
              <div className="glass-card" style={{ border: `1px solid ${faultStates.harness_fault ? 'var(--neon-red)' : 'var(--border-glass)'}` }}>
                <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.5rem' }}><Volume2 style={{ color: 'var(--neon-orange)' }} /> Harness Mismatch</h3>
                <button className="btn-secondary" style={{ width: '100%', background: faultStates.harness_fault ? 'var(--neon-red)' : 'transparent', color: faultStates.harness_fault ? '#000' : '#fff' }} onClick={() => toggleFault('harness_fault')}>
                  {faultStates.harness_fault ? "FAULT ACTIVE" : "INJECT FAULT"}
                </button>
              </div>

            </div>
          </div>
        )}
      </main>
    </div>
  );
}
