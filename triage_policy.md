# MediCare AI Agent — Triage Policy Document

This document is the "knowledge base" the agent's Tool node consults to
classify a patient's reported symptoms into an urgency category and
recommend a next action. It is a **simplified, educational** policy
document for a student project demo — it is NOT real medical guidance
and the agent must always tell the user to consult a licensed
professional.

## Category 1: EMERGENCY — Call emergency services immediately
Trigger keywords/phrases (non-exhaustive):
- chest pain, pressure in chest
- difficulty breathing, can't breathe, shortness of breath (severe)
- sudden numbness or weakness on one side of body
- slurred speech, confusion, sudden severe headache
- severe uncontrolled bleeding
- loss of consciousness, fainting with injury
- suicidal thoughts, self-harm intent

Action: Skip normal flow. Immediately respond with an emergency
escalation message directing the user to call local emergency
services right now, and do not attempt to give further triage advice.

## Category 2: URGENT — See a doctor within 24 hours
Examples:
- persistent high fever (3+ days)
- severe pain that is worsening
- vomiting that won't stop
- injury with suspected fracture (no severe bleeding)

Action: Recommend booking an urgent-care or same/next-day
appointment; do not attempt home-treatment advice.

## Category 3: ROUTINE — Schedule a regular appointment
Examples:
- mild recurring headache
- ongoing mild joint pain
- skin rash without fever
- routine follow-up questions

Action: Recommend scheduling a routine appointment with the
appropriate specialist/GP.

## Category 4: SELF-CARE / MONITOR
Examples:
- mild cold symptoms, sore throat without fever
- minor fatigue, occasional mild headache

Action: Suggest general rest/hydration/monitoring language only
(no medication names or dosages) and to seek care if symptoms
worsen or persist beyond a few days.

## Standing Disclaimer (must be appended to every non-emergency response)
"This is an AI assistant for informational triage routing only. It
is not a medical diagnosis. Please consult a licensed healthcare
professional for any medical concerns."
