# MediCare AI Agent 🩺 (Final — Groq)

Agentic AI patient symptom triage & appointment-guidance assistant.
Built for the **IBM SkillsBuild x AICTE Internship — Agentic AI project**.

- **SDG alignment:** SDG 3 — Good Health and Well-being
- **Architecture:** Planner → PolicyTool → Validator → Action (LangGraph),
  same 4-node action-oriented pattern as the SmartSupport AI project.
- **LLM:** Groq (free tier, `llama-3.1-8b-instant`)
- **Frontend:** Streamlit
- **Deployment:** Streamlit Cloud (free)

## Why Groq instead of Gemini
Google AI Studio API keys can hit `429`/quota errors on the free tier
(especially if the model name is deprecated or Pro-tier). Groq's free
tier is simpler and has worked reliably for this project, so this is
the **final** version.

## How it works
1. **Planner** — classifies the patient's message into EMERGENCY / URGENT /
   ROUTINE / SELF-CARE.
2. **PolicyTool** — reads `triage_policy.md` and produces a
   `Decision: ... / Reason: ...` line.
3. **Validator** — checks the decision is well-formed; retries once if not.
4. **Action** — writes a short guidance email, **sends a real email** to
   the patient via Gmail SMTP, and logs the case to `decision_log.txt`.

⚠️ Educational demo only — never provides a diagnosis, and always tells
the user to consult a licensed professional.

## Project structure
```
medicare-ai-agent/
├── agent.py               # module version — used by app.py (Streamlit) and importable in Colab
├── medicare_agent_colab.py # standalone script version — input()-based, for quick Colab testing
├── app.py                  # Streamlit UI
├── triage_policy.md        # Knowledge base the PolicyTool node consults
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚠️ Security — do this before pushing to GitHub
Never hardcode your real `GROQ_API_KEY`, `EMAIL_SENDER`, or
`EMAIL_APP_PASSWORD` inside `agent.py` or `medicare_agent_colab.py`.
- In `agent.py`, these are already read from environment variables —
  nothing to change.
- In `medicare_agent_colab.py`, the key/password fields are left blank
  on purpose — fill them in your **local Colab session only**, never
  commit a filled-in copy to GitHub.
- If you ever pasted a real key/password into a chat, notebook, or
  committed file, **revoke and regenerate it** immediately:
  - Groq: https://console.groq.com/keys
  - Gmail App Password: https://myaccount.google.com/apppasswords

## 1. Push to GitHub
```bash
cd medicare-ai-agent
git init
git add .
git commit -m "MediCare AI Agent — final Groq version"
git branch -M main
git remote add origin https://github.com/<your-username>/medicare-ai-agent.git
git push -u origin main
```

## 2. Run locally (optional, before deploying)
```bash
pip install -r requirements.txt
cp .env.example .env        # fill in your real Groq key + Gmail creds
streamlit run app.py
```

## 3. Deploy on Streamlit Cloud (free)
1. Go to https://share.streamlit.io → **New app**.
2. Select your GitHub repo, branch `main`, main file `app.py`.
3. Open **⋮ → Settings → Secrets** and paste:
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   EMAIL_SENDER = "your_gmail_address@gmail.com"
   EMAIL_APP_PASSWORD = "your_16_char_app_password"
   ```
4. Click **Deploy**. You'll get a public URL like
   `https://medicare-ai-agent-<random>.streamlit.app` — submit this
   link alongside your PPT.

### Getting the two keys
- **Groq API key (free):** https://console.groq.com/keys
- **Gmail App Password:**
  1. Turn on 2-Step Verification on the Gmail account you'll send from.
  2. Go to https://myaccount.google.com/apppasswords
  3. Create an app password for "Mail" → use the 16-character code as
     `EMAIL_APP_PASSWORD` (not your real Gmail password).

If the email vars aren't set, the app still runs fine — it just skips
the send step and says so in the result.

## 4. Run in Google Colab (for testing/screenshots)
Option A — quick script (`medicare_agent_colab.py`):
```python
!pip install langgraph langchain-groq
```
Upload `medicare_agent_colab.py` and `triage_policy.md` to `/content/`,
fill in your `GROQ_API_KEY`/`SENDER_EMAIL`/`SENDER_APP_PASSWORD` at the
top of the file, then run it — it will prompt for patient details via
`input()`.

Option B — import the module version (`agent.py`):
```python
import os
os.environ["GROQ_API_KEY"] = "your_groq_key"
os.environ["EMAIL_SENDER"] = "your_gmail@gmail.com"
os.environ["EMAIL_APP_PASSWORD"] = "your_16_char_app_password"

from agent import run_agent
print(run_agent("I have a mild headache", "Test Patient", "test@example.com", "9999999999"))
```

## Sample test inputs
- "I have chest pain and can't breathe properly" → EMERGENCY
- "I've had a high fever for 3 days and keep vomiting" → URGENT
- "I have a mild headache that comes and goes" → ROUTINE
- "just feeling a bit tired and have a sore throat" → SELF-CARE

## Internship submission checklist
- [x] Working agent code (`agent.py`)
- [ ] Live deployed app (Streamlit Cloud link)
- [ ] GitHub repo
- [ ] Test case screenshots
- [ ] Lean Canvas (PDF)
- [ ] Concept Note (PDF)
- [ ] PPT
