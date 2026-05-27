# ⚡ ResumeIQ - AI-Powered Resume Analyzer

A full-stack web application that analyzes your resume against a job description using the Anthropic Claude API. Get a match score, identify missing keywords, receive rewritten bullet points, and ATS optimization tips — instantly.

**Live Demo:** [your-deployment-url-here]

---

## ✦ Features

- **AI Match Scoring** — Claude scores resume-to-JD fit from 0–100
- **Missing Keywords** — highlights skills and terms absent from your resume
- **Bullet Rewrites** — suggests improved, impact-driven versions of your bullets
- **ATS Tips** — actionable advice to pass Applicant Tracking Systems
- **PDF Upload** — supports direct resume PDF upload
- **Clean UI** — Fun pastel themed, responsive React frontend

---

## 🏗 Architecture

```
┌─────────────────┐        ┌──────────────────┐        ┌─────────────────┐
│   React Frontend │  HTTP  │   Flask Backend   │  API   │  Anthropic      │
│   (Vercel)       │───────▶│   (AWS EC2)       │───────▶│  Claude Sonnet  │
└─────────────────┘        └──────────────────┘        └─────────────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │   AWS S3 Bucket   │
                           │  (resume storage) │
                           └──────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Vite, CSS3 |
| Backend | Python, Flask, REST API |
| AI | Anthropic Claude Sonnet API |
| Infrastructure | AWS (EC2, S3), Terraform |
| DevOps | Docker, GitHub Actions CI/CD |
| Deployment | Vercel (frontend), AWS EC2 (backend) |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional)
- Anthropic API Key → [console.anthropic.com](https://console.anthropic.com)

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/resumeiq.git
cd resumeiq
```

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
# Add your ANTHROPIC_API_KEY to .env
python app.py
```

### 3. Frontend setup
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

App runs at `http://localhost:3000`

### 4. Run with Docker Compose
```bash
# Add your API key to backend/.env first
docker-compose up --build
```

---

## ☁️ Infrastructure (Terraform)

Provisions AWS resources: EC2 instance, S3 bucket, security groups, Elastic IP.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## CI/CD

GitHub Actions pipeline on every push to `main`:
1. Python lint (flake8)
2. React build check
3. Docker build
4. Deploy to AWS EC2

---

## 📁 Project Structure

```
resumeiq/
├── backend/
│   ├── app.py              # Flask API
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   └── App.css         # Styles
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── terraform/
│   ├── main.tf             # AWS resources
│   ├── variables.tf
│   └── outputs.tf
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions
├── docker-compose.yml
└── README.md
```

---

## Author

**Marie Lou Panthagani** · [linkedin.com/in/marie-lou-panthagani](https://linkedin.com/in/marie-lou-panthagani) · [github.com/mlray27](https://github.com/mlray27)
