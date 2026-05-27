import { useState, useRef } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const LOADING_MSGS = [
  "feeding your resume to the AI overlords...",
  "calculating your chances (praying for you)...",
  "comparing you to 847 other applicants...",
  "finding polite ways to say 'needs work'...",
  "consulting the job market crystal ball...",
  "asking claude if you're cooked...",
];

const EMPTY_JOKES = [
  "your resume is about to get roasted. lovingly.",
  "drop your resume. we've seen worse. probably.",
  "the job market is rough. let's at least fix your resume.",
  "rejected 5 times this week? same. let's try again.",
  "we won't judge. the ATS will, but we won't.",
];

const SCORE_CAPTIONS = (score) => {
  if (score >= 85) return "ngl this actually slaps 👀";
  if (score >= 70) return "solid. not hired yet, but solid.";
  if (score >= 50) return "it's giving... potential. buried potential.";
  if (score >= 30) return "the good news: you have a pulse.";
  return "okay so we have some work to do 😬";
};

const SECTION_JOKES = {
  strengths: "things keeping you out of the reject pile",
  missing: "words the ATS is crying about rn",
  rewrites: "your bullets but make them hireable",
  ats: "how to trick the robot before the human ghosts you",
};

function ScoreRing({ score }) {
  const radius = 54;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (score / 100) * circ;
  const color = score >= 75 ? "#4ade80" : score >= 50 ? "#fbbf24" : "#f87171";

  return (
    <div className="score-ring-wrap">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="#f0ebe4" strokeWidth="12" />
        <circle
          cx="70" cy="70" r={radius} fill="none"
          stroke={color} strokeWidth="12"
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 70 70)"
          style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1)" }}
        />
      </svg>
      <div className="score-label">
        <span className="score-number" style={{ color }}>{score}</span>
        <span className="score-sub">/ 100</span>
      </div>
    </div>
  );
}

function Tag({ text, type }) {
  return <span className={`tag tag-${type}`}>{text}</span>;
}

function Section({ title, joke, icon, children }) {
  return (
    <div className="result-section">
      <h3 className="section-title">
        <span className="section-icon">{icon}</span>{title}
      </h3>
      {joke && <p className="section-joke">{joke}</p>}
      {children}
    </div>
  );
}

export default function App() {
  const [jd, setJd] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [emptyJoke] = useState(EMPTY_JOKES[Math.floor(Math.random() * EMPTY_JOKES.length)]);
  const fileRef = useRef();
  const loadingRef = useRef(null);

  const handleFile = (f) => {
    if (f && (f.type === "application/pdf" || f.type === "text/plain")) {
      setFile(f);
      setError("");
    } else {
      setError("PDF or .txt only. we're picky like the recruiters.");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const analyze = async () => {
    if (!jd.trim()) return setError("paste a job description first. yes, the whole thing.");
    if (!file) return setError("we need the resume too. that's kind of the whole point.");
    setError("");
    setLoading(true);
    setResult(null);

    let i = 0;
    setLoadingMsg(LOADING_MSGS[0]);
    loadingRef.current = setInterval(() => {
      i = (i + 1) % LOADING_MSGS.length;
      setLoadingMsg(LOADING_MSGS[i]);
    }, 2000);

    try {
      const form = new FormData();
      form.append("job_description", jd);
      form.append("resume", file);

      const res = await fetch(`${API_URL}/analyze`, { method: "POST", body: form });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (e) {
      setError(e.message || "something broke. classic.");
    } finally {
      clearInterval(loadingRef.current);
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">ResumeIQ</span>
        </div>
        <p className="tagline">because the job market won't fix itself</p>
        <p className="tagline-sub">AI-powered resume analysis · powered by desperation and machine learning</p>
      </header>

      <main className="main">
        <div className="input-panel">

          <div className="input-card">
            <label className="input-label">
              <span className="label-num">01</span>
              the job you're manifesting
            </label>
            <textarea
              className="jd-input"
              placeholder="paste the job description here. yes, requirements too. especially the ones that say '10 years of experience in a 3-year-old framework'..."
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              rows={12}
            />
          </div>

          <div className="input-card">
            <label className="input-label">
              <span className="label-num">02</span>
              your resume (it'll be okay)
            </label>
            <div
              className={`dropzone ${dragOver ? "drag-over" : ""} ${file ? "has-file" : ""}`}
              onClick={() => fileRef.current.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              <input
                ref={fileRef} type="file" accept=".pdf,.txt"
                style={{ display: "none" }}
                onChange={(e) => handleFile(e.target.files[0])}
              />
              {file ? (
                <>
                  <span className="file-icon">📄</span>
                  <span className="file-name">{file.name}</span>
                  <span className="file-change">click to swap · we won't tell</span>
                </>
              ) : (
                <>
                  <span className="upload-icon">📎</span>
                  <span className="upload-text">drop resume here</span>
                  <span className="upload-sub">PDF or TXT · it's seen worse, we promise</span>
                </>
              )}
            </div>
          </div>

          {error && <div className="error-msg">⚠ {error}</div>}

          <button
            className={`analyze-btn ${loading ? "loading" : ""}`}
            onClick={analyze}
            disabled={loading}
          >
            {loading ? (
              <><span className="spinner" />{loadingMsg}</>
            ) : (
              <><span>⚡</span> roast my resume (constructively)</>
            )}
          </button>

          <p className="disclaimer">no resumes are harmed in this process. egos may vary.</p>
        </div>

        {result && (
          <div className="results-panel">

            <div className="score-card">
              <ScoreRing score={result.match_score} />
              <div className="score-info">
                <h2 className="score-title">match score</h2>
                <p className="score-caption">{SCORE_CAPTIONS(result.match_score)}</p>
                <p className="score-summary">{result.summary}</p>
              </div>
            </div>

            <Section title="strengths" joke={SECTION_JOKES.strengths} icon="✦">
              <ul className="strength-list">
                {result.strengths?.map((s, i) => (
                  <li key={i} className="strength-item">
                    <span className="check">✓</span>{s}
                  </li>
                ))}
              </ul>
            </Section>

            <Section title="missing keywords" joke={SECTION_JOKES.missing} icon="◈">
              <div className="tags-wrap">
                {result.missing_keywords?.map((k, i) => (
                  <Tag key={i} text={k} type="missing" />
                ))}
              </div>
            </Section>

            <Section title="bullet rewrites" joke={SECTION_JOKES.rewrites} icon="✎">
              {result.improvement_suggestions?.map((s, i) => (
                <div key={i} className="rewrite-card">
                  <div className="rewrite-before">
                    <span className="rewrite-label">before (it's okay)</span>
                    <p>{s.original}</p>
                  </div>
                  <div className="rewrite-arrow">→</div>
                  <div className="rewrite-after">
                    <span className="rewrite-label">after (much better)</span>
                    <p>{s.improved}</p>
                  </div>
                  <div className="rewrite-reason">💡 {s.reason}</div>
                </div>
              ))}
            </Section>

            <Section title="ATS tips" joke={SECTION_JOKES.ats} icon="◎">
              <ul className="ats-list">
                {result.ats_tips?.map((t, i) => (
                  <li key={i} className="ats-item">
                    <span className="ats-num">{String(i + 1).padStart(2, "0")}</span>{t}
                  </li>
                ))}
              </ul>
            </Section>

            <div className="footer-joke">
              you've made it this far. that's more than most. go apply. 🚀
            </div>

          </div>
        )}

        {!result && !loading && (
          <div className="empty-state">
            <div className="empty-icon">◈</div>
            <p>{emptyJoke}</p>
            <span>paste JD + upload resume → hit the button</span>
            <span className="empty-sub">powered by Claude AI · built by someone also job hunting</span>
          </div>
        )}
      </main>

      <footer className="footer">
        Built with React · Flask · Gemini AI · Docker · Terraform · AWS · and a concerning amount of coffee
      </footer>
    </div>
  );
}
