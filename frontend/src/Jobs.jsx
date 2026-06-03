import { useState, useEffect } from "react";

const RESULTS_URL = "https://raw.githubusercontent.com/mlray27/resumeiq/main/jobagent/results/latest_jobs.json";

const scoreColor = (s) => s >= 85 ? "#16a34a" : s >= 70 ? "#ca8a04" : "#dc2626";
const scoreBg    = (s) => s >= 85 ? "#dcfce7" : s >= 70 ? "#fef9c3" : "#fee2e2";

export default function Jobs() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");

  useEffect(() => {
    fetch(RESULTS_URL)
      .then(r => { if (!r.ok) throw new Error("No results yet"); return r.json(); })
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return (
    <div className="jobs-state">
      <span className="spinner" style={{ borderTopColor: "#a855f7" }} />
      <p>Loading fresh matches...</p>
    </div>
  );

  if (error) return (
    <div className="jobs-state">
      <div className="empty-icon">◈</div>
      <p>No job results yet</p>
      <span>Agent runs at 9AM, 2PM and 7PM EST daily</span>
    </div>
  );

  return (
    <div className="jobs-panel">
      <div className="jobs-header">
        <div>
          <h2 className="jobs-title">Today's Matches</h2>
          <p className="jobs-meta">Last updated: {data.last_updated}</p>
        </div>
        <div className="jobs-stats">
          <div className="stat">
            <span className="stat-num">{data.total_found}</span>
            <span className="stat-label">scanned</span>
          </div>
          <div className="stat">
            <span className="stat-num" style={{ color: "#a855f7" }}>{data.total_matched}</span>
            <span className="stat-label">matched</span>
          </div>
        </div>
      </div>

      <div className="jobs-list">
        {data.jobs.length === 0 ? (
          <div className="jobs-state">
            <p>No matches above 70% this batch</p>
            <span>Check back at the next run!</span>
          </div>
        ) : (
          data.jobs.map((job, i) => (
            <div key={i} className="job-card">
              <div className="job-score" style={{ background: scoreBg(job.score), color: scoreColor(job.score) }}>
                {job.score}
              </div>
              <div className="job-info">
                <p className="job-title">{job.title}</p>
                <p className="job-meta">{job.source} · {job.date}</p>
                <p className="job-reason">💡 {job.reason}</p>
              </div>
              <a href={job.link} target="_blank" rel="noreferrer" className="job-apply">
                Apply →
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
