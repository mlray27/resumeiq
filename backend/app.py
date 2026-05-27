from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv
import PyPDF2
import io

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

def extract_text_from_pdf(file_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def call_gemini(prompt):
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3}
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        job_description = request.form.get("job_description", "")
        resume_file = request.files.get("resume")

        if not job_description or not resume_file:
            return jsonify({"error": "Both job description and resume are required."}), 400

        file_bytes = resume_file.read()
        if resume_file.filename.lower().endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_bytes)
        else:
            resume_text = file_bytes.decode("utf-8")

        prompt = f"""You are an expert technical recruiter and resume coach specializing in Software Engineer and AI roles.

Analyze the following resume against the job description and return a JSON object with exactly this structure:

{{
  "match_score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "missing_keywords": ["<keyword 1>", "<keyword 2>", "<keyword 3>", "<keyword 4>", "<keyword 5>"],
  "improvement_suggestions": [
    {{
      "original": "<original bullet or section text>",
      "improved": "<rewritten version>",
      "reason": "<why this change helps>"
    }},
    {{
      "original": "<original bullet or section text>",
      "improved": "<rewritten version>",
      "reason": "<why this change helps>"
    }}
  ],
  "ats_tips": ["<tip 1>", "<tip 2>", "<tip 3>"]
}}

IMPORTANT: Return ONLY the JSON object. No markdown, no backticks, no explanation.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}"""

        raw = call_gemini(prompt)

        # Strip markdown fences if Gemini adds them
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip()

        result = json.loads(clean)
        return jsonify(result)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return jsonify({"error": f"Gemini API error: {error_body}"}), 500
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse AI response: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
