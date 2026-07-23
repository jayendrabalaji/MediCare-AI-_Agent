"""
MediCare AI Agent — Streamlit App (Groq)
==========================================
Run locally:   streamlit run app.py
Deploy free:   push this repo to GitHub, then deploy on
               https://streamlit.io/cloud pointing at app.py,
               and add GROQ_API_KEY / EMAIL_SENDER /
               EMAIL_APP_PASSWORD as Secrets (see README.md).
"""

import streamlit as st
from agent import run_agent

st.set_page_config(page_title="MediCare AI Agent", page_icon="🩺", layout="centered")

st.title("🩺 MediCare AI Agent")
st.caption("Patient Symptom Triage & Appointment Guidance Agent — SDG 3: Good Health")

st.markdown(
    """
This is a student project demo of an **agentic AI system**
(Planner → PolicyTool → Validator → Action) built with LangGraph +
Groq. It classifies your symptoms into an urgency category and
emails you (and logs) the guidance — same action-oriented pattern as
the SmartSupport AI project.

⚠️ **This tool does not provide medical diagnoses.** For real
symptoms, please consult a licensed healthcare professional, and
call emergency services for any emergency.
"""
)

st.subheader("Your details")
col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Name")
    patient_phone = st.text_input("Phone number")
with col2:
    patient_email = st.text_input("Email")

st.subheader("Symptoms")
user_input = st.text_area(
    "Describe how you're feeling:",
    placeholder="e.g. I've had a mild headache since yesterday...",
    height=100,
)

if st.button("Get Guidance", type="primary"):
    if not user_input.strip():
        st.warning("Please describe your symptoms first.")
    else:
        with st.spinner("Agent running: Planner → PolicyTool → Validator → Action..."):
            try:
                result = run_agent(
                    user_input,
                    patient_name=patient_name,
                    patient_email=patient_email,
                    patient_phone=patient_phone,
                )
                st.markdown("### Result")
                st.text(result)
            except Exception as e:
                st.error(f"Something went wrong: {e}")

st.divider()
st.caption(
    "Built for the IBM SkillsBuild AICTE Internship — Agentic AI project. "
    "Architecture: Planner → PolicyTool → Validator → Action (LangGraph + Groq)."
)
