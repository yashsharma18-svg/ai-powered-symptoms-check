import streamlit as st
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# ── Environment ─────────────────────────────────────────────────────────────
load_dotenv()

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Symptom Checker",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Constants ────────────────────────────────────────────────────────────────
TRIAGE_LEVELS = {
    "EMERGENCY": {
        "label": "🚨 Emergency — Call 911 / Go to ER Now",
        "color": "#FF4B4B",
        "bg": "#fff0f0",
        "border": "#FF4B4B",
        "advice": (
            "Your symptoms may indicate a life-threatening condition. "
            "Call emergency services (911) immediately or go to the nearest "
            "emergency room. Do not drive yourself."
        ),
    },
    "SEE_DOCTOR": {
        "label": "⚠️ See a Doctor — Schedule an Appointment Soon",
        "color": "#FF8C00",
        "bg": "#fff8e6",
        "border": "#FF8C00",
        "advice": (
            "Your symptoms warrant professional medical evaluation within "
            "24–48 hours. Contact your primary care physician or visit an "
            "urgent-care clinic. Do not ignore worsening symptoms."
        ),
    },
    "SELF_CARE": {
        "label": "✅ Self-Care — Manageable at Home",
        "color": "#28a745",
        "bg": "#f0fff4",
        "border": "#28a745",
        "advice": (
            "Your symptoms appear mild and can typically be managed at home "
            "with rest, hydration, and over-the-counter remedies. Monitor "
            "your condition. Seek medical attention if symptoms worsen or "
            "persist beyond 3–5 days."
        ),
    },
}

SYSTEM_PROMPT = """You are a highly knowledgeable medical triage assistant. 
Your role is to analyze patient-reported symptoms and provide:
1. A triage recommendation
2. Possible related conditions
3. Specific self-care advice or urgency guidance

IMPORTANT RULES:
- Always recommend professional medical consultation for serious symptoms
- Never provide definitive diagnoses
- Be empathetic and clear
- Consider age, duration, and severity when mentioned
- Flag any red-flag symptoms immediately (chest pain, difficulty breathing, sudden severe headache, signs of stroke, uncontrolled bleeding, etc.)

You MUST respond ONLY with a valid JSON object in this exact format (no markdown, no extra text):
{
  "triage_level": "EMERGENCY" | "SEE_DOCTOR" | "SELF_CARE",
  "triage_reasoning": "<1-2 sentence explanation of triage decision>",
  "possible_conditions": [
    {"name": "<condition name>", "likelihood": "High|Moderate|Low", "brief": "<one sentence description>"},
    ...
  ],
  "red_flags_detected": ["<flag1>", "<flag2>"] or [],
  "self_care_tips": ["<tip1>", "<tip2>", ...],
  "when_to_escalate": "<clear instruction on when to seek higher care>",
  "disclaimer": "This is not a medical diagnosis. Always consult a qualified healthcare professional."
}"""


# ── Gemini helpers ────────────────────────────────────────────────────────────
MODEL_NAME = "models/gemini-3.6-flash"


def get_gemini_client(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=1500,
        ),
        system_instruction=SYSTEM_PROMPT,
    ), MODEL_NAME


def analyze_symptoms(model, symptoms: str, age: str, duration: str, severity: int) -> dict:
    user_message = f"""
Patient Information:
- Age group: {age}
- Symptom duration: {duration}
- Self-reported severity (1–10): {severity}
- Symptoms described: {symptoms}

Please analyze these symptoms and return the JSON response as specified.
"""
    response = model.generate_content(user_message)
    raw = response.text.strip()

    # Strip possible markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


# ── UI helpers ───────────────────────────────────────────────────────────────
def render_triage_badge(level: str):
    info = TRIAGE_LEVELS.get(level, TRIAGE_LEVELS["SEE_DOCTOR"])
    st.markdown(
        f"""
        <div style="
            background:{info['bg']};
            border-left: 6px solid {info['border']};
            border-radius: 6px;
            padding: 16px 20px;
            margin: 12px 0;
        ">
            <span style="font-size:1.25rem; font-weight:700; color:{info['color']};">
                {info['label']}
            </span>
            <p style="margin:8px 0 0 0; color:#333;">{info['advice']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_conditions(conditions: list):
    if not conditions:
        return
    st.subheader("🔍 Possible Related Conditions")
    likelihood_colors = {"High": "🔴", "Moderate": "🟡", "Low": "🟢"}
    for c in conditions:
        icon = likelihood_colors.get(c.get("likelihood", "Low"), "⚪")
        with st.expander(f"{icon} {c.get('name', 'Unknown')} — {c.get('likelihood', '')} likelihood"):
            st.write(c.get("brief", ""))


def render_self_care(tips: list):
    if not tips:
        return
    st.subheader("💊 Self-Care & Next Steps")
    for tip in tips:
        st.markdown(f"- {tip}")


def render_red_flags(flags: list):
    if not flags:
        return
    st.subheader("🚩 Red Flags Detected")
    for flag in flags:
        st.error(f"⚠️ {flag}")


def render_escalation(when: str):
    if not when:
        return
    st.info(f"**When to escalate:** {when}")


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/stethoscope.png",
        width=72,
    )
    st.title("AI Symptom Checker")
    st.caption("Powered by Google Gemini 3.6 Flash")
    st.divider()

    st.subheader("🔑 API Configuration")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        placeholder="AIza...",
        help="Get your free key at https://aistudio.google.com/app/apikey",
    )

    st.divider()
    st.subheader("ℹ️ About")
    st.markdown(
        """
        This tool uses **Google Gemini 1.5 Flash** to analyze your 
        symptoms and provide a triage recommendation:

        - 🚨 **Emergency** — Seek immediate care  
        - ⚠️ **See a Doctor** — Visit within 24–48 hrs  
        - ✅ **Self-Care** — Manage at home  

        > **Disclaimer:** This app is for informational purposes only 
        > and does not constitute medical advice. Always consult a 
        > licensed healthcare professional.
        """
    )


# ── Main content ──────────────────────────────────────────────────────────────
st.title("🩺 AI-Powered Symptom Checker")
st.markdown(
    "Describe your symptoms below and receive an AI-powered triage recommendation, "
    "possible conditions, and actionable guidance."
)
st.warning(
    "⚠️ **Medical Disclaimer:** This tool is for informational purposes only. "
    "It does not replace professional medical advice, diagnosis, or treatment."
)
st.divider()

# ── Input form ────────────────────────────────────────────────────────────────
with st.form("symptom_form", clear_on_submit=False):
    st.subheader("📋 Describe Your Symptoms")

    symptoms_input = st.text_area(
        "What symptoms are you experiencing?",
        placeholder=(
            "e.g., I have had a severe headache for 2 days, "
            "accompanied by nausea, sensitivity to light, and a stiff neck..."
        ),
        height=140,
        help="Be as detailed as possible — include location, quality, and any associated symptoms.",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        age_group = st.selectbox(
            "Age Group",
            ["Child (0–12)", "Teen (13–17)", "Adult (18–64)", "Senior (65+)"],
            index=2,
        )

    with col2:
        duration = st.selectbox(
            "Duration",
            [
                "Just started (< 1 hour)",
                "A few hours",
                "1–2 days",
                "3–7 days",
                "More than a week",
                "Chronic / recurring",
            ],
            index=2,
        )

    with col3:
        severity = st.slider(
            "Severity (1 = mild, 10 = worst)",
            min_value=1,
            max_value=10,
            value=5,
            help="Rate how severe your symptoms feel overall.",
        )

    submitted = st.form_submit_button("🔍 Analyze Symptoms", use_container_width=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
if submitted:
    if not api_key_input:
        st.error("❌ Please enter your Gemini API key in the sidebar.")
        st.stop()

    if not symptoms_input.strip():
        st.error("❌ Please describe your symptoms before submitting.")
        st.stop()

    if len(symptoms_input.strip()) < 10:
        st.error("❌ Please provide a more detailed description of your symptoms.")
        st.stop()

    with st.spinner("🤖 Analyzing your symptoms with Gemini AI..."):
        try:
            model, resolved_model = get_gemini_client(api_key_input)
            result = analyze_symptoms(
                model,
                symptoms=symptoms_input,
                age=age_group,
                duration=duration,
                severity=severity,
            )
        except json.JSONDecodeError:
            st.error(
                "❌ The AI returned an unexpected response format. "
                "Please try again or rephrase your symptoms."
            )
            st.stop()
        except Exception as exc:
            err = str(exc)
            if "API_KEY_INVALID" in err or "API key" in err.lower():
                st.error("❌ Invalid Gemini API key. Please check your key and try again.")
            elif "quota" in err.lower() or "429" in err:
                st.error("❌ API quota exceeded. Please wait a moment and try again.")
            else:
                st.error(f"❌ An error occurred: {err}")
            st.stop()

    st.divider()
    st.subheader("📊 Triage Results")
    st.caption(f"🤖 Model used: `{resolved_model}`")

    # Triage badge
    triage_level = result.get("triage_level", "SEE_DOCTOR")
    render_triage_badge(triage_level)

    # Reasoning
    reasoning = result.get("triage_reasoning", "")
    if reasoning:
        st.markdown(f"**Why this triage level?** {reasoning}")

    st.divider()

    # Red flags (shown prominently)
    red_flags = result.get("red_flags_detected", [])
    render_red_flags(red_flags)

    # Possible conditions
    conditions = result.get("possible_conditions", [])
    render_conditions(conditions)

    # Self-care tips
    tips = result.get("self_care_tips", [])
    render_self_care(tips)

    # Escalation
    escalation = result.get("when_to_escalate", "")
    render_escalation(escalation)

    st.divider()

    # Disclaimer
    disclaimer = result.get(
        "disclaimer",
        "This is not a medical diagnosis. Always consult a qualified healthcare professional.",
    )
    st.caption(f"📋 {disclaimer}")

    # Raw JSON expander for transparency
    with st.expander("🔧 View raw AI response (JSON)"):
        st.json(result)
