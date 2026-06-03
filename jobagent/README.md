# ⚡ JobAgent — Automated Job Matching Agent

Scrapes fresh job postings 3x daily, scores them against Marie Lou's resume using Gemini AI,
sends a Gmail digest, and displays matches on the ResumeIQ dashboard.

---

## How It Works

```
9AM / 2PM / 7PM EST
        ↓
GitHub Actions triggers agent.py
        ↓
Scrapes: Indeed RSS + RemoteOK + Google Jobs (SerpAPI) + Wellfound
        ↓
Gemini AI scores each job against resume (filters ≥ 70%)
        ↓
Saves results → jobagent/results/latest_jobs.json
        ↓
Sends Gmail digest with ranked matches + apply links
        ↓
ResumeIQ dashboard reads results and displays them
```

---

## Setup (one time)

### 1. Get your API keys

| Key | Where to get it | Free? |
|---|---|---|
| `GEMINI_API_KEY` | aistudio.google.com/apikey | ✅ Free |
| `SERPAPI_KEY` | serpapi.com | ✅ 100 searches/month free |
| `GMAIL_APP_PASS` | See below | ✅ Free |

### 2. Gmail App Password
1. Go to myaccount.google.com → Security
2. Enable 2-Factor Authentication
3. Search "App passwords" → Create one named "JobAgent"
4. Copy the 16-character password

### 3. Add secrets to GitHub
Go to your `resumeiq` GitHub repo → Settings → Secrets → Actions → New secret:

- `GEMINI_API_KEY`
- `GMAIL_USER` → `marieloup.mlp@gmail.com`
- `GMAIL_APP_PASS` → your 16-char app password
- `SERPAPI_KEY`

### 4. Copy files to your resumeiq repo
```
resumeiq/
├── jobagent/
│   ├── agent.py
│   ├── requirements.txt
│   ├── results/          ← auto-created by agent
│   └── .github/
│       └── workflows/
│           └── jobagent.yml
└── frontend/
    └── src/
        ├── Jobs.jsx      ← add to frontend
        └── jobs.css      ← add to frontend
```

### 5. Update App.jsx
Add the Jobs tab to your existing ResumeIQ app — see instructions below.

### 6. Run manually to test
GitHub repo → Actions → "JobAgent — 3x Daily" → Run workflow

---

## Adding Jobs Tab to ResumeIQ

In `frontend/src/App.jsx`, add at the top:
```jsx
import Jobs from "./Jobs.jsx";
import "./jobs.css";
```

Add tab state:
```jsx
const [activeTab, setActiveTab] = useState("analyzer");
```

Add nav tabs before `<main>`:
```jsx
<div className="nav-tabs">
  <button className={`nav-tab ${activeTab === "analyzer" ? "active" : ""}`}
    onClick={() => setActiveTab("analyzer")}>⚡ Resume Analyzer</button>
  <button className={`nav-tab ${activeTab === "jobs" ? "active" : ""}`}
    onClick={() => setActiveTab("jobs")}>🎯 Job Matches</button>
</div>
```

Wrap `<main>` content conditionally:
```jsx
{activeTab === "analyzer" ? (
  <main className="main">
    {/* existing analyzer content */}
  </main>
) : (
  <main className="main" style={{ gridTemplateColumns: "1fr" }}>
    <Jobs />
  </main>
)}
```
