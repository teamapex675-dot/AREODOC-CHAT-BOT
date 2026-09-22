# ═══════════════════════════════════════════════════════════════
# AeroDx AI Chatbot — Streamlit Edition
# ═══════════════════════════════════════════════════════════════
import streamlit as st
import time

# ── Simulated AeroDx data ──────────────────────────────────────
HEALTH_INDEX = 87
MOTORS = {
    "M1": {"current": 10.1, "residual": 0.08},
    "M2": {"current": 10.3, "residual": -0.03},
    "M3": {"current": 10.0, "residual": 0.05},
    "M4": {"current": 11.6, "residual": 2.35}
}
FUEL = {"z_score": 3.2, "status": "SENSOR ANOMALY"}
ALERTS = [
    {"time": "14:03:12", "type": "Component", "message": "Motor-4 ESC overcurrent (z=2.35)", "confidence": 87},
    {"time": "14:03:26", "type": "Physics veto", "message": "Confirmed", "confidence": 100},
]
RUL = {"low": 18, "high": 25, "unit": "operating hours"}

# ── Chatbot logic ──────────────────────────────────────────────
def generate_response(user_input):
    text = user_input.lower()

    if any(w in text for w in ["hi", "hello", "hey"]):
        return "Hello! I'm the AeroDx Health Assistant. Ask me about flight health, faults, sensors, or remaining life."

    if any(w in text for w in ["health", "status", "how are you"]):
        return (f"Current Health Index: **{HEALTH_INDEX}**/100\n\n"
                f"Battery: 78% | Altitude: 119.5 m | Speed: 4.2 m/s\n\n"
                f"Alert level: **DEGRADING** – see fault details.")

    if any(w in text for w in ["motor", "esc", "propeller"]):
        if "4" in text or "m4" in text:
            return (f"Motor 4:\n- Current: **{MOTORS['M4']['current']} A** (expected ~10.2 A)\n"
                    f"- Residual: **{MOTORS['M4']['residual']} σ** (threshold: 2σ)\n"
                    f"- Diagnosis: **ESC-4 circuit fault** (87% confidence)\n"
                    f"- Evidence: z=2.35, persistence 4.2s, torque imbalance +0.14 N·m")
        else:
            summary = "\n".join(f"{name}: {data['current']} A (residual {data['residual']:+}σ)" for name, data in MOTORS.items())
            return f"All motor currents:\n{summary}"

    if any(w in text for w in ["fault", "error", "issue", "problem", "alert"]):
        if not ALERTS:
            return "No active faults. All systems nominal."
        response = "**Active Alerts:**\n\n"
        for a in ALERTS:
            response += f"- {a['time']}: {a['message']} (confidence {a['confidence']}%)\n"
        response += "\nRecommendation: Motor-4 ESC circuit inspection advised."
        return response

    if any(w in text for w in ["fuel", "sensor"]):
        return (f"Fuel system:\n- Fuel sensor z-score: **{FUEL['z_score']}**\n- Status: **{FUEL['status']}**\n\n"
                "The fuel sensor disagrees with 3 other systems + physics model → flagged as sensor fault.\n"
                "Mission can continue – fuel telemetry is being ignored.")

    if any(w in text for w in ["remaining", "rul", "life"]):
        return f"Estimated Remaining Useful Life: **{RUL['low']}–{RUL['high']} {RUL['unit']}**\nForecast based on current degradation trend and operating profile."

    if any(w in text for w in ["sensor", "imu", "gps", "baro"]):
        return "All sensor trust scores:\n- IMU-A: 88%\n- IMU-B: 92%\n- GPS: 71%\n- Baro: 85%\n- ESC-4: 34% (low)"

    if any(w in text for w in ["how", "work", "what is aerodx", "explain"]):
        return ("AeroDx uses a **physics-based digital twin** to predict what each sensor *should* read.\n"
                "The difference (residual) is analyzed by AI to localize faults.\n"
                "It also provides calibrated confidence (e.g., 87%) and mission replay.")

    if any(w in text for w in ["replay", "log", "history"]):
        return ("Mission replay available. Last events:\n"
                "14:03:12 – Motor-4 anomaly detected\n"
                "14:03:25 – AI alert (87%)\n"
                "14:03:27 – Land-now advisory sent")

    return "I can help with: health, motor/fault, fuel/sensor, remaining life, sensors, how AeroDx works, or replay."

# ── Streamlit UI ───────────────────────────────────────────────
st.set_page_config(page_title="AeroDx AI Chatbot", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background-color: #ffffff; }
    .stTextInput input { background-color: #f0f2f5; border: 1px solid #1b4f99; }
    .stChatMessage { background-color: #f8f9fa; border-radius: 10px; padding: 8px; margin-bottom: 8px; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💬 AeroDx AI Chatbot")
st.caption("Your drone's health co-pilot — ask anything about flight diagnostics.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box
if prompt := st.chat_input("Ask about health, faults, sensors..."):
    # User message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Bot response with typing effect
    response = generate_response(prompt)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = f"🤖 {response}"
        typed = ""
        for char in full_response:
            time.sleep(0.01)
            typed += char
            placeholder.markdown(typed + "▌")
        placeholder.markdown(typed)
    st.session_state.messages.append({"role": "assistant", "content": typed})
