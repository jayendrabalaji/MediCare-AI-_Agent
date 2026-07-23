# =========================================================
# MediCare AI Agent — FINAL (Groq API, action-oriented)
# Planner -> PolicyTool -> Validator -> ACTION (send real email + log)
# Same pattern as SmartSupport AI, wrapped as an importable
# function so it works in Colab AND in app.py (Streamlit).
# =========================================================

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
import os
import smtplib
from email.mime.text import MIMEText
import datetime

# -------------------------
# 0. API Key & Email setup — read from environment (.env locally,
#    Streamlit Secrets when deployed). NEVER hardcode real keys here.
# -------------------------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
SENDER_EMAIL = os.environ.get("EMAIL_SENDER", "")
SENDER_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "")

_llm = None


def _get_llm():
    """Lazily create the Groq client so importing this file doesn't
    crash before the key is set."""
    global _llm
    if _llm is None:
        if not GROQ_API_KEY:
            return None
        _llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=GROQ_API_KEY,
            temperature=0,
        )
    return _llm


# -------------------------
# Load policy document (same folder as this file)
# -------------------------
POLICY_PATH = os.path.join(os.path.dirname(__file__), "triage_policy.md")
with open(POLICY_PATH, "r") as f:
    POLICY_TEXT = f.read()


# -------------------------
# 1. Agent State
# -------------------------
class PatientState(TypedDict):
    patient_name: str
    patient_email: str
    patient_phone: str
    user_input: str
    category: Optional[str]
    policy_decision: Optional[str]
    retries: int
    decision_status: Optional[str]
    final_answer: Optional[str]
    action_status: Optional[str]


# -------------------------
# 2. Planner Node (Perception)
# -------------------------
def planner(state: PatientState):
    llm = _get_llm()
    if llm is None:
        return {"category": "ROUTINE", "retries": state.get("retries", 0)}

    prompt = f"""
    You are a patient triage classifier.
    Read the patient's symptom message and identify ONE category:
    EMERGENCY / URGENT / ROUTINE / SELF-CARE

    Patient message: "{state['user_input']}"

    Reply with ONLY the category name.
    """
    response = llm.invoke(prompt)
    category = response.content.strip()

    return {
        "category": category,
        "retries": state.get("retries", 0),
    }


# -------------------------
# 3. Tool Node (Reasoning using Policy)
# -------------------------
def policy_tool(state: PatientState):
    llm = _get_llm()
    if llm is None:
        return {"policy_decision": "Decision: Routine\nReason: Groq API key not configured — safe default applied."}

    prompt = f"""
    You are a patient triage agent. Use ONLY the policy below to decide.

    POLICY:
    {POLICY_TEXT}

    Patient message: "{state['user_input']}"
    Category identified: {state['category']}

    Decide: Approved, Escalated, or Routine.
    (Approved = self-care/routine guidance is enough,
     Escalated = notify clinic immediately for URGENT/EMERGENCY,
     Routine = schedule a normal appointment)
    Give a one-line reason based on the policy.

    Reply in this EXACT format:
    Decision: <Approved/Escalated/Routine>
    Reason: <one line reason>
    """
    response = llm.invoke(prompt)
    return {"policy_decision": response.content.strip()}


# -------------------------
# 4. Validator Node
# -------------------------
def validator(state: PatientState):
    decision_text = state["policy_decision"]

    if "Decision:" in decision_text and "Reason:" in decision_text:
        return {"decision_status": "approved"}

    if state["retries"] >= 1:
        return {"decision_status": "stop"}

    return {
        "decision_status": "retry",
        "retries": state["retries"] + 1,
    }


# -------------------------
# 5. ACTION Node (Reply text + REAL email send + log)
# -------------------------
def action_node(state: PatientState):
    llm = _get_llm()
    if llm is not None:
        reply_prompt = f"""
        Write a short, calm, reassuring patient-guidance email reply based on
        this triage decision:
        {state['policy_decision']}
        Category: {state['category']}

        Patient's original message: "{state['user_input']}"
        Keep it under 60 words. Do not include subject line.
        Always end by reminding the patient this is not a diagnosis and to
        consult a licensed professional, and for EMERGENCY category tell
        them to call emergency services immediately.
        """
        response = llm.invoke(reply_prompt)
        reply_body = response.content.strip()
    else:
        reply_body = (
            "Thanks for your message. Based on general guidance, please "
            "book a routine appointment. This is not a diagnosis — "
            "consult a licensed professional. (Groq API key not "
            "configured, so this is a generic fallback reply.)"
        )

    # ---- Try to send a REAL email ----
    action_status = "Not attempted"
    if SENDER_EMAIL and SENDER_APP_PASSWORD and state.get("patient_email"):
        try:
            msg = MIMEText(reply_body)
            msg["Subject"] = f"MediCare AI — {state['category']} triage update"
            msg["From"] = SENDER_EMAIL
            msg["To"] = state["patient_email"]

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, state["patient_email"], msg.as_string())
            server.quit()
            action_status = "✅ Email sent successfully"
        except Exception as e:
            action_status = f"⚠️ Email not sent — {str(e)[:80]}"
    else:
        action_status = "(Email not configured — set EMAIL_SENDER/EMAIL_APP_PASSWORD to enable)"

    # ---- Log the decision (simulates clinic system update) ----
    try:
        with open("decision_log.txt", "a") as log:
            log.write(
                f"[{datetime.datetime.now()}] Patient: {state.get('patient_name')} | "
                f"To: {state.get('patient_email')} | Phone: {state.get('patient_phone')} | "
                f"Category: {state['category']} | {state['policy_decision']} | "
                f"Action: {action_status}\n"
            )
    except Exception:
        pass

    final_text = f"""📌 Category: {state['category']}
📋 {state['policy_decision']}
🤖 Action Taken: {action_status}

📩 Email Body:
{reply_body}"""

    return {"final_answer": final_text, "action_status": action_status}


# -------------------------
# 6. Build the Graph
# -------------------------
def build_graph():
    graph = StateGraph(PatientState)

    graph.add_node("Planner", planner)
    graph.add_node("PolicyTool", policy_tool)
    graph.add_node("Validator", validator)
    graph.add_node("Action", action_node)

    graph.set_entry_point("Planner")
    graph.add_edge("Planner", "PolicyTool")
    graph.add_edge("PolicyTool", "Validator")

    graph.add_conditional_edges(
        "Validator",
        lambda state: state["decision_status"],
        {
            "approved": "Action",
            "retry": "Planner",
            "stop": "Action",
        },
    )

    graph.add_edge("Action", END)
    return graph.compile()


_agent = None


def run_agent(user_input: str, patient_name: str = "", patient_email: str = "", patient_phone: str = "") -> str:
    """Used by app.py (Streamlit) and can also be imported in Colab."""
    global _agent
    if _agent is None:
        _agent = build_graph()

    result = _agent.invoke({
        "patient_name": patient_name,
        "patient_email": patient_email,
        "patient_phone": patient_phone,
        "user_input": user_input,
        "retries": 0,
    })
    return result["final_answer"]


# -------------------------
# 7. Local/Colab manual test — only runs if you execute this file directly
# -------------------------
if __name__ == "__main__":
    patient_name = input("Enter patient's name: ")
    patient_email = input("Enter patient's email address: ")
    patient_phone = input("Enter patient's phone number: ")
    user_text = input("Describe your symptoms: ")

    print("\n===== MediCare AI Agent Response =====")
    print(run_agent(user_text, patient_name, patient_email, patient_phone))
