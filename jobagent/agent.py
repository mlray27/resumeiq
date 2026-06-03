"""
JobAgent — Scrapes fresh job postings 3x daily, scores against Marie Lou's resume,
sends Gmail digest + saves results for dashboard.
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")
GMAIL_USER      = os.getenv("GMAIL_USER")        # your gmail address
GMAIL_APP_PASS  = os.getenv("GMAIL_APP_PASS")    # gmail app password
TO_EMAIL        = "marieloup.mlp@gmail.com"
SERPAPI_KEY     = os.getenv("SERPAPI_KEY")        # free at serpapi.com
RESULTS_FILE    = "results/latest_jobs.json"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

RESUME_SUMMARY = """
Marie Lou Panthagani — Software Engineer + AI
MS Computer Science, NYU Courant (graduated Dec 2025)
Current: Software Engineer Intern at Effexoft — building agentic AI workflows using Anthropic Claude API,
Python backend services, Airflow ETL pipelines, Docker, AWS (S3, Lambda), dbt, SQL optimization.

Skills: Python, JavaScript, TypeScript, React.js, Flask, FastAPI, Node.js, PyTorch, TensorFlow,
LangChain, RAG, Anthropic Claude API, Gemini AI, PostgreSQL, MongoDB, Redis, Snowflake, Kafka,
AWS, GCP, Docker, Kubernetes, Terraform, Ansible, GitHub Actions, CI/CD, Apache Spark, Airflow, dbt.

Target roles: Software Engineer, AI Engineer, Full Stack Engineer, Backend Engineer, ML Engineer.
Location: New Jersey / New York / Remote.
"""

TARGET_KEYWORDS = [
    "software engineer", "AI engineer", "backend engineer",
    "full stack engineer", "machine learning engineer", "python developer",
    "ML engineer", "AI developer", "LLM engineer"
]

# ── Scrapers ─────────────────────────────────────────────────────────────────

def fetch_indeed_rss():
    """Indeed RSS — today's SWE/AI jobs in NY/NJ/Remote"""
    jobs = []
    queries = [
        "software+engineer+AI",
        "python+backend+engineer",
        "machine+learning+engineer"
    ]
    for q in queries:
        url = f"https://www.indeed.com/rss?q={q}&l=New+York&fromage=1&sort=date"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                root = ET.fromstring(r.read())
                for item in root.findall(".//item"):
                    title    = item.findtext("title", "").strip()
                    link     = item.findtext("link", "").strip()
                    desc     = item.findtext("description", "").strip()
                    pub_date = item.findtext("pubDate", "").strip()
                    if title and link:
                        jobs.append({
                            "title": title, "link": link,
                            "description": desc[:500],
                            "source": "Indeed", "date": pub_date
                        })
        except Exception as e:
            print(f"Indeed RSS error ({q}): {e}")
    return jobs


def fetch_remoteok():
    """RemoteOK — free public API, real-time remote jobs"""
    jobs = []
    tags = ["python", "react", "machine-learning", "ai", "backend"]
    seen = set()
    for tag in tags:
        url = f"https://remoteok.com/api?tag={tag}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())[1:]  # first item is metadata
                for job in data[:10]:
                    job_id = job.get("id", "")
                    if job_id in seen:
                        continue
                    seen.add(job_id)
                    # Only today's jobs
                    epoch = job.get("epoch", 0)
                    posted = datetime.fromtimestamp(epoch, tz=timezone.utc)
                    if (datetime.now(timezone.utc) - posted).days > 0:
                        continue
                    jobs.append({
                        "title": job.get("position", ""),
                        "link": job.get("url", f"https://remoteok.com/l/{job_id}"),
                        "description": job.get("description", "")[:500],
                        "source": "RemoteOK",
                        "date": posted.strftime("%Y-%m-%d")
                    })
        except Exception as e:
            print(f"RemoteOK error ({tag}): {e}")
    return jobs


def fetch_google_jobs():
    """Google Jobs via SerpAPI — today only"""
    if not SERPAPI_KEY:
        print("No SERPAPI_KEY set, skipping Google Jobs")
        return []
    jobs = []
    queries = ["software engineer AI New York", "python backend engineer remote"]
    for q in queries:
        params = urllib.parse.urlencode({
            "engine": "google_jobs",
            "q": q,
            "chips": "date_posted:today",
            "api_key": SERPAPI_KEY
        })
        url = f"https://serpapi.com/search?{params}"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read())
                for job in data.get("jobs_results", [])[:10]:
                    jobs.append({
                        "title": job.get("title", ""),
                        "link": job.get("share_link", ""),
                        "description": job.get("description", "")[:500],
                        "source": "Google Jobs",
                        "date": job.get("detected_extensions", {}).get("posted_at", "today")
                    })
        except Exception as e:
            print(f"Google Jobs error ({q}): {e}")
    return jobs


def fetch_wellfound():
    """Wellfound (AngelList) — startup SWE/AI roles via their API"""
    jobs = []
    # Wellfound public job search endpoint
    roles = ["software-engineer", "machine-learning-engineer", "ai-engineer"]
    for role in roles:
        url = f"https://wellfound.com/role/r/{role}"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            })
            # Wellfound returns job listings — parse what's available
            with urllib.request.urlopen(req, timeout=10) as r:
                content = r.read().decode("utf-8")
                # Basic extraction of job titles/links from response
                if "jobTitle" in content or "position" in content:
                    jobs.append({
                        "title": f"{role.replace('-', ' ').title()} roles",
                        "link": url,
                        "description": "Browse latest startup roles on Wellfound",
                        "source": "Wellfound",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
        except Exception as e:
            print(f"Wellfound error ({role}): {e}")
    return jobs


# ── AI Scoring ────────────────────────────────────────────────────────────────

def score_job(job):
    """Score a job against Marie Lou's resume using Gemini"""
    prompt = f"""You are a technical recruiter. Score how well this candidate matches this job posting.

CANDIDATE PROFILE:
{RESUME_SUMMARY}

JOB POSTING:
Title: {job['title']}
Source: {job['source']}
Description: {job['description']}

Return ONLY a JSON object:
{{
  "score": <integer 0-100>,
  "reason": "<one sentence why this is or isn't a good match>",
  "apply": <true if score >= 70, false otherwise>
}}

No markdown, no backticks, just JSON."""

    try:
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1}
        }).encode("utf-8")

        req = urllib.request.Request(
            GEMINI_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            clean = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
    except Exception as e:
        print(f"Scoring error for '{job['title']}': {e}")
        return {"score": 0, "reason": "Could not score", "apply": False}


# ── Email ─────────────────────────────────────────────────────────────────────

def send_email(matched_jobs, batch_time):
    if not GMAIL_USER or not GMAIL_APP_PASS:
        print("Gmail credentials not set, skipping email")
        return

    total = len(matched_jobs)
    subject = f"⚡ JobAgent — {total} fresh matches · {batch_time}"

    # Build HTML email
    rows = ""
    for j in matched_jobs:
        score = j['score']
        color = "#16a34a" if score >= 85 else "#ca8a04" if score >= 70 else "#dc2626"
        rows += f"""
        <tr>
          <td style="padding:12px;border-bottom:1px solid #f0f0f0">
            <a href="{j['link']}" style="font-weight:600;color:#1a1a2e;text-decoration:none">{j['title']}</a>
            <br><span style="font-size:12px;color:#888">{j['source']} · {j.get('date','today')}</span>
          </td>
          <td style="padding:12px;border-bottom:1px solid #f0f0f0;text-align:center">
            <span style="font-weight:700;color:{color};font-size:18px">{score}</span>
          </td>
          <td style="padding:12px;border-bottom:1px solid #f0f0f0;font-size:13px;color:#555">{j['reason']}</td>
          <td style="padding:12px;border-bottom:1px solid #f0f0f0;text-align:center">
            <a href="{j['link']}" style="background:#7c3aed;color:white;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:13px">Apply</a>
          </td>
        </tr>"""

    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px">
      <div style="background:linear-gradient(135deg,#1a1a2e,#7c3aed);padding:24px;border-radius:12px;margin-bottom:24px">
        <h1 style="color:white;margin:0;font-size:24px">⚡ JobAgent Digest</h1>
        <p style="color:rgba(255,255,255,0.8);margin:8px 0 0">{batch_time} · {total} matches above 70%</p>
      </div>
      <table style="width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1)">
        <thead>
          <tr style="background:#f8f8f8">
            <th style="padding:12px;text-align:left;font-size:13px;color:#888">JOB</th>
            <th style="padding:12px;text-align:center;font-size:13px;color:#888">SCORE</th>
            <th style="padding:12px;text-align:left;font-size:13px;color:#888">WHY IT FITS</th>
            <th style="padding:12px;font-size:13px;color:#888">APPLY</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
      <p style="text-align:center;color:#aaa;font-size:12px;margin-top:24px">
        JobAgent · running 3x daily · built by Marie Lou Panthagani
      </p>
    </body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(html, "html"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())
        print(f"✅ Email sent: {total} matches")
    except Exception as e:
        print(f"Email error: {e}")


# ── Save results for dashboard ────────────────────────────────────────────────

def save_results(matched_jobs, all_jobs, batch_time):
    os.makedirs("results", exist_ok=True)

    # Load existing results to append
    existing = []
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE) as f:
                existing = json.load(f).get("jobs", [])
        except:
            existing = []

    # Keep last 100 jobs max
    combined = matched_jobs + existing
    combined = combined[:100]

    output = {
        "last_updated": batch_time,
        "total_found": len(all_jobs),
        "total_matched": len(matched_jobs),
        "jobs": combined
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"✅ Saved {len(matched_jobs)} matched jobs to {RESULTS_FILE}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    batch_time = datetime.now().strftime("%B %d, %Y · %I:%M %p EST")
    print(f"\n{'='*50}")
    print(f"⚡ JobAgent running — {batch_time}")
    print(f"{'='*50}\n")

    # 1. Fetch from all sources
    print("📡 Fetching jobs...")
    all_jobs = []
    all_jobs += fetch_indeed_rss()
    all_jobs += fetch_remoteok()
    all_jobs += fetch_google_jobs()
    all_jobs += fetch_wellfound()

    # Deduplicate by title+source
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['title'].lower()}_{job['source']}"
        if key not in seen and job['title']:
            seen.add(key)
            unique_jobs.append(job)

    print(f"📋 Found {len(unique_jobs)} unique jobs across all sources\n")

    # 2. Score each job
    print("🤖 Scoring jobs with Gemini AI...")
    matched_jobs = []
    for i, job in enumerate(unique_jobs):
        print(f"  Scoring {i+1}/{len(unique_jobs)}: {job['title'][:50]}...")
        result = score_job(job)
        if result.get("apply"):
            matched_jobs.append({
                **job,
                "score": result["score"],
                "reason": result["reason"]
            })

    matched_jobs.sort(key=lambda x: x["score"], reverse=True)
    print(f"\n✅ {len(matched_jobs)} jobs matched (score ≥ 70)\n")

    # 3. Save results for dashboard
    save_results(matched_jobs, unique_jobs, batch_time)

    # 4. Send email digest
    if matched_jobs:
        print("📧 Sending email digest...")
        send_email(matched_jobs, batch_time)
    else:
        print("📭 No matches this batch — no email sent")

    print(f"\n{'='*50}")
    print(f"✅ JobAgent complete — {batch_time}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
