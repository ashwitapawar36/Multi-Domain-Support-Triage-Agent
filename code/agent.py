import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv


load_dotenv(dotenv_path="../hack.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

SYSTEM_PROMPT = """
You are a support triage agent for three products: HackerRank, Claude (Anthropic), and Visa.

Your job: read the user's support ticket and the relevant documentation, then produce a JSON response.

Rules:
1. Only use information from the provided documentation. Do NOT use outside knowledge or invent policies.
2. If the issue involves: fraud, unauthorized transactions, account compromise, billing disputes, legal threats, data breaches — ESCALATE.
3. If the issue is clearly out of scope, irrelevant, or malicious — reply with an "out of scope" message, status=replied, request_type=invalid.
4. If the documentation doesn't cover the issue at all — escalate.
5. Be concise and professional in your response.

Output ONLY valid JSON with these exact keys:
{
  "status": "replied" or "escalated",
  "product_area": "string (e.g. Billing, Account Access, Assessments, Fraud, API, etc.)",
  "response": "string (user-facing message)",
  "justification": "string (internal reasoning for your decision)",
  "request_type": "product_issue" or "feature_request" or "bug" or "invalid"
}
"""

def triage_ticket(issue, subject, company, relevant_docs, log_file=None):
    prompt = f"""{SYSTEM_PROMPT}

Support Ticket:
Subject: {subject or '(no subject)'}
Company: {company or 'Unknown'}
Issue: {issue}

Relevant documentation from the support corpus:
{relevant_docs}

Triage this ticket and respond with JSON only.
"""

    if log_file:
        log_file.write(f"\n[USER]\n{prompt}\n")

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "response_mime_type": "application/json"
            }
        )
        raw = response.text.strip()

    except Exception as e:
        raw = ""
        print(f"  [agent] Gemini error: {e}")

    if log_file:
        log_file.write(f"\n[ASSISTANT]\n{raw}\n{'='*60}\n")

    match = re.search(r'\{.*\}', raw, re.DOTALL)
    clean = match.group(0) if match else raw.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "status": "escalated",
            "product_area": "Unknown",
            "response": "Unable to process this ticket automatically. Please escalate to a human agent.",
            "justification": f"JSON parse error. Raw: {raw[:200]}",
            "request_type": "product_issue"
        }