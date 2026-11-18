
import streamlit as st
import random
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="AI Network Monitoring System", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: Inter, Segoe UI, sans-serif !important;
}

.stApp{
background: linear-gradient(180deg,#FFFFFF 0%,#F5F7FA 100%);
}

.block-container{
padding-top:1.4rem !important;
padding-bottom:0.8rem !important;
max-width:98% !important;
}

.dashboard-card,.section-card{
background:white;
border-radius:14px;
padding:12px;
box-shadow:0 2px 8px rgba(0,0,0,.04);
}

.section-title{
color:#2563EB;
font-size:16px;
font-weight:700;
margin-bottom:10px;
}

.kpi-box{
padding:10px;
border-radius:12px;
background:white;
text-align:center;
margin-bottom:6px;
border:1px solid #E2E8F0;
}

.kpi-low{
border:2px solid #EF4444 !important;
background:white !important;
}

.kpi-ai{
border:2px solid #22C55E !important;
}

.kpi-qrl{
border:3px solid #15803D !important;
}

.kpi-name{
font-size:12px;
font-weight:600;
color:#64748B;
}

.kpi-value{
font-size:18px;
font-weight:700;
color:#111827;
}
</style>
""", unsafe_allow_html=True)

defaults = {
    "issue_loaded": False,
    "baseline_data": None,
    "ai_data": None,
    "qrl_data": None,
    "show_summary": False,
    "mode": "Baseline"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "reset_radio" not in st.session_state:
    st.session_state.reset_radio = False

# Force Baseline selection before radio widget is created
if st.session_state.reset_radio:
    st.session_state.pop("radio_mode", None)
    st.session_state["radio_mode"] = "Baseline"
    st.session_state.mode = "Baseline"
    st.session_state.reset_radio = False

THRESHOLDS = {
    "RSRP": -90,
    "RSRQ": -10,
    "SINR": 15,
    "Latency": 50,
    "PacketLoss": 3,
    "Throughput": 100,
    "CQI": 10,
    "Congestion": 1,
}

def num(v):
    try:
        return float(str(v).replace("dBm","").replace("dB","").replace("ms","").replace("Mbps","").replace("%","").strip())
    except:
        return 0

def is_low(k,v):
    n = num(v)
    if k in ["RSRP","RSRQ"]:
        return n < THRESHOLDS[k]
    if k in ["SINR","Throughput","CQI"]:
        return n < THRESHOLDS[k]
    return n > THRESHOLDS[k]

def generate_degraded_kpis():
    return {
        "RSRP": f"{random.randint(-115,-90)} dBm",
        "RSRQ": f"{random.randint(-20,-12)} dB",
        "SINR": f"{random.randint(1,12)} dB",
        "Latency": f"{random.randint(70,150)} ms",
        "PacketLoss": f"{round(random.uniform(4,12),2)}%",
        "Throughput": f"{round(random.uniform(30,250),2)} Mbps",
        "CQI": str(random.randint(1,8)),
        "Congestion": str(random.randint(2,6))
    }

def generate_ai_kpis(base):
    return {"RSRP":"-85 dBm","RSRQ":"-10 dB","SINR":"18 dB","Latency":"45 ms",
            "PacketLoss":"2%","Throughput":"120 Mbps","CQI":"12","Congestion":"1"}

def generate_qrl_kpis(ai):
    return {"RSRP":"-75 dBm","RSRQ":"-7 dB","SINR":"28 dB","Latency":"20 ms",
            "PacketLoss":"0.5%","Throughput":"180 Mbps","CQI":"15","Congestion":"0"}

def render_section(title,data,compare=None,mode_type=None):
    st.markdown(f"<div class='section-card'><div class='section-title'>{title}</div>", unsafe_allow_html=True)

    cols = st.columns(8,gap="small")

    for i,(k,v) in enumerate(data.items()):
        cls = "kpi-box"

        if is_low(k,v):
            cls += " kpi-low"

        if compare and compare.get(k) != v:
            if mode_type == "AI":
                cls += " kpi-ai"
            elif mode_type == "QRL":
                cls += " kpi-qrl"

        with cols[i]:
            st.markdown(
                f"""
                <div class="{cls}">
                    <div class="kpi-name">{k}</div>
                    <div class="kpi-value">{v}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class='dashboard-card'>
<h2>📡 AI Network Monitoring System</h2>
<p>Telecom AI + Quantum RL Optimization Platform</p>
</div>
""", unsafe_allow_html=True)

left,right=st.columns([1.2,4])

with left:
    if st.session_state.reset_radio:
        if "radio_mode" in st.session_state:
            del st.session_state["radio_mode"]
        st.session_state.reset_radio = False

    mode = st.radio(
        "Modes",
        ["Baseline","AI","Quantum RL"],
        key="radio_mode"
    )

    st.session_state.mode = mode

with right:
    c1,c2,c3=st.columns([1,1,4])

    with c1:
        if st.button("🔍 Find Issue",use_container_width=True):
            st.session_state.issue_loaded=True
            st.session_state.baseline_data=generate_degraded_kpis()
            st.session_state.ai_data=None
            st.session_state.qrl_data=None
            st.session_state.show_summary=False
            st.session_state.mode="Baseline"
            st.session_state.reset_radio=True
            st.rerun()

    with c2:
        if st.button("▶ Next Issue",use_container_width=True):
            st.session_state.issue_loaded=True
            st.session_state.baseline_data=generate_degraded_kpis()
            st.session_state.ai_data=None
            st.session_state.qrl_data=None
            st.session_state.show_summary=False
            st.session_state.mode="Baseline"
            st.session_state.reset_radio=True
            st.rerun()

if st.session_state.issue_loaded and st.session_state.baseline_data:

    render_section("🚨 Baseline Network Parameters", st.session_state.baseline_data)

    if st.session_state.mode == "AI":
        if st.session_state.ai_data is None:
            st.session_state.ai_data = generate_ai_kpis(st.session_state.baseline_data)

    elif st.session_state.mode == "Quantum RL":
        if st.session_state.ai_data is None:
            st.session_state.ai_data = generate_ai_kpis(st.session_state.baseline_data)
        if st.session_state.qrl_data is None:
            st.session_state.qrl_data = generate_qrl_kpis(st.session_state.ai_data)

    show_ai = st.session_state.mode in ["AI","Quantum RL"] and st.session_state.ai_data is not None
    show_qrl = st.session_state.mode == "Quantum RL" and st.session_state.qrl_data is not None

    if show_ai:
        render_section(
            "🤖 AI Optimized Parameters",
            st.session_state.ai_data,
            compare=st.session_state.baseline_data,
            mode_type="AI"
        )

    if show_qrl:
        render_section(
            "⚛️ Quantum RL Optimized Parameters",
            st.session_state.qrl_data,
            compare=st.session_state.baseline_data,
            mode_type="QRL"
        )

        if st.button("📊 View Optimization Summary", use_container_width=True):
            st.session_state.show_summary = True

    if st.session_state.show_summary:
        x=np.linspace(0,10,80)
        baseline=40+1.2*np.sin(x)+0.4*np.cos(2*x)
        ai=68+1.5*np.sin(x+0.8)
        qrl=90+1.8*np.sin(x+1.5)

        fig=go.Figure()
        fig.add_trace(go.Scatter(x=x,y=baseline,name="Baseline",mode="lines"))
        fig.add_trace(go.Scatter(x=x,y=ai,name="AI Optimized",mode="lines"))
        fig.add_trace(go.Scatter(x=x,y=qrl,name="Quantum RL",mode="lines"))

        fig.update_layout(height=260,paper_bgcolor="white",plot_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
