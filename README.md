# 🩺 AI-Powered Symptom Checker

A Streamlit application that analyzes user-reported symptoms and returns a **triage recommendation** (Self-Care / See a Doctor / Emergency), a list of **possible related conditions**, and **actionable guidance** — all powered by **Google Gemini 1.5 Flash**.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🤖 AI Engine | Google Gemini 1.5 Flash |
| 🎯 Triage Levels | Emergency · See a Doctor · Self-Care |
| 🔍 Conditions | Possible related conditions with likelihood ratings |
| 🚩 Red Flags | Automatic detection of life-threatening symptom patterns |
| 💊 Self-Care Tips | Tailored next-step guidance |
| 📋 Transparency | Raw JSON AI response viewable in-app |
| 🔒 Secure | API key entered at runtime, never stored |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd "Ai powered symptoms check"
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

**Option A — `.env` file (recommended for local dev):**
```bash
cp .env.example .env
# Edit .env and replace the placeholder with your real key
```

**Option B — Enter at runtime:**  
Paste your key directly into the sidebar **API Key** field when the app runs.

> Get a free Gemini API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 5. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## 🌐 Deploy to Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch (`main`), and main file (`app.py`).
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "AIza..."
   ```
5. Click **Deploy**.

---

## 🗂️ Project Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## 🧩 How It Works

```
User Input (symptoms + age + duration + severity)
        │
        ▼
  Gemini 1.5 Flash  ◄──  Structured system prompt
        │
        ▼
  JSON Response
  ├── triage_level       → EMERGENCY | SEE_DOCTOR | SELF_CARE
  ├── triage_reasoning   → Why this level was chosen
  ├── possible_conditions → Name + likelihood + brief
  ├── red_flags_detected → Life-threatening patterns
  ├── self_care_tips     → Actionable home guidance
  └── when_to_escalate   → Clear escalation instructions
        │
        ▼
  Streamlit UI renders results
```

---

## ⚠️ Disclaimer

This application is for **informational and educational purposes only**. It does **not** constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for any medical concerns.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.32.0 | Web UI framework |
| `google-generativeai` | ≥ 0.5.0 | Gemini AI SDK |
| `python-dotenv` | ≥ 1.0.0 | `.env` file support |
