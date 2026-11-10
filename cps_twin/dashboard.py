"""Streamlit digital-twin dashboard for simulation telemetry."""
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from cps_twin.cli import run_simulation

st.set_page_config(page_title="CPS Digital Twin", page_icon="🤖", layout="wide")
st.title("AI Cyber-Physical Systems | Digital Twin")
st.caption("Synthetic industrial inspection-robot simulation — not a certified safety system.")

with st.sidebar:
    st.header("Scenario controls")
    steps = st.slider("Simulation steps", 100, 2000, 600, 100)
    seed = st.number_input("Random seed", min_value=0, max_value=99999, value=7)
    uploaded = st.file_uploader("Or load JSONL telemetry", type=["jsonl", "txt"])
    run = st.button("Run simulation", type="primary")

if uploaded is not None:
    records = [json.loads(line) for line in uploaded.getvalue().decode("utf-8").splitlines() if line.strip()]
    df = pd.DataFrame(records)
elif run:
    with st.spinner("Running closed-loop simulation..."):
        records = run_simulation(int(steps), int(seed), output=None)
    df = pd.DataFrame(records)
    st.session_state["telemetry"] = df
elif "telemetry" in st.session_state:
    df = st.session_state["telemetry"]
else:
    st.info("Run a scenario or load a JSONL telemetry file to inspect the digital twin.")
    st.stop()

if df.empty:
    st.warning("No telemetry records found.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Simulation duration", f"{df.sim_time_s.max():.1f} s")
c2.metric("Hazard alerts", int(df.hazard_detected.sum()))
c3.metric("Safety interventions", int(df.safety_override.sum()))
c4.metric("Distance from origin", f"{((df.pose_x.iloc[-1]-df.pose_x.iloc[0])**2 + (df.pose_y.iloc[-1]-df.pose_y.iloc[0])**2)**0.5:.2f} m")

left, right = st.columns(2)
with left:
    st.subheader("Robot trajectory")
    fig = px.line(df, x="pose_x", y="pose_y", color="hazard_detected", title="2-D facility position", labels={"pose_x":"X (m)", "pose_y":"Y (m)", "hazard_detected":"Hazard"})
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Sensor and AI response")
    sensor = px.line(df, x="sim_time_s", y=["gas_ppm", "temperature_c"], title="Sensor readings over time")
    st.plotly_chart(sensor, use_container_width=True)

st.subheader("Hazard probability and safety actions")
prob = px.line(df, x="sim_time_s", y="hazard_probability", title="ML hazard probability")
prob.add_hline(y=0.72, line_dash="dash", annotation_text="Safety threshold")
st.plotly_chart(prob, use_container_width=True)
alerts = df[df.safety_override | df.hazard_detected][["sim_time_s", "hazard_probability", "obstacle_range_m", "safety_override", "override_reason"]]
st.subheader("Events requiring attention")
st.dataframe(alerts.tail(100), use_container_width=True)
st.download_button("Download displayed telemetry", df.to_json(orient="records", lines=True), "cps_telemetry.jsonl", "application/jsonl")
