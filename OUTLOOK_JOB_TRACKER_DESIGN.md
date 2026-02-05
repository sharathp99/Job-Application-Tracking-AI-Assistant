# Job Application Tracking Agent from Outlook Emails

## High-Level System Architecture

### Core Components

1. **Outlook Ingestion Service**
   - Connects to Microsoft Graph API using OAuth 2.0.
   - Pulls new emails from Outlook (via delta queries).
   - Normalizes email content (HTML → text) and metadata.

2. **Classification & Extraction Pipeline**
   - **Rule-based classifier** for fast, deterministic tagging.
   - **LLM/NLP classifier** for ambiguous cases.
   - **Entity extraction** for company, role, recruiter, etc.

3. **Application Store**
   - Relational database (PostgreSQL or SQLite for local).
   - Stores job records, email records, and status history.

4. **Agent Orchestrator**
   - Coordinates ingestion, classification, extraction, and updates.
   - Runs on schedule (cron, Celery beat, or GitHub Actions).
   - Detects duplicates and status changes.

5. **Reporting & UI Layer**
   - Generates filtered lists (applied, rejected, interview).
   - Optional dashboard (Streamlit, React, or simple CLI reports).

### Data Flow

```
Microsoft 365 Inbox → Graph API → Ingestion Service →
Classifier/Extractor → Database → Reports/Dashboard
```

---

## Step-by-Step Implementation Plan

1. **Set up Microsoft Graph API access**
   - Register Azure app.
   - Configure `Mail.Read` and `offline_access` permissions.
   - Implement OAuth token flow.

2. **Build email ingestion module**
   - Use Graph `messages` endpoint with delta queries.
   - Parse subject, sender, body, timestamp, attachments.

3. **Implement classification logic**
   - Start with keyword-based rules.
   - Add LLM fallback for ambiguous emails.
   - Store classification confidence.

4. **Implement extraction logic**
   - Extract company and role using NER rules + LLM.
   - Normalize dates and job IDs.
   - Store recruiter name if present.

5. **Build storage layer**
   - Define SQL schema.
   - Implement upsert logic and duplicate detection.

6. **Create reporting queries**
   - Generate applied / rejected / pending lists.
   - Create weekly summaries.

7. **Automation & scheduling**
   - Run hourly/daily with cron or task scheduler.
   - Use delta tokens to fetch only new emails.

---

## Sample Data Schema (SQL)

### `job_applications`
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| company_name | TEXT | Normalized company |
| job_title | TEXT | Role title |
| job_id | TEXT | Reference/job ID |
| location | TEXT | Job location |
| recruiter_name | TEXT | Recruiter if found |
| applied_date | DATE | Application submission |
| current_status | TEXT | applied/rejected/interview/etc |
| last_email_id | TEXT | Last linked email |
| created_at | TIMESTAMP | Insert time |
| updated_at | TIMESTAMP | Update time |

### `emails`
| Field | Type | Description |
|-------|------|-------------|
| id | TEXT | Outlook message ID |
| subject | TEXT | Email subject |
| sender | TEXT | Sender address |
| received_at | TIMESTAMP | Date received |
| body_text | TEXT | Normalized body |
| classification | TEXT | Classified category |
| confidence | FLOAT | Classifier confidence |
| job_application_id | UUID | Foreign key |

### `status_history`
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| job_application_id | UUID | FK to job |
| status | TEXT | New status |
| source_email_id | TEXT | Trigger email |
| changed_at | TIMESTAMP | Timestamp |

---

## Example Email Classification Logic

### Rule-Based Keywords

```python
RULES = {
    "rejected": ["we regret", "unfortunately", "not moving forward"],
    "interview": ["schedule", "interview", "phone screen"],
    "assessment": ["assessment", "coding challenge", "test"],
    "applied": ["application received", "thank you for applying"],
    "recruiter_outreach": ["your background", "opportunity", "reach out"],
}

def classify_with_rules(subject, body):
    text = f"{subject} {body}".lower()
    for label, keywords in RULES.items():
        if any(kw in text for kw in keywords):
            return label, 0.85
    return "unknown", 0.2
```

### LLM Fallback

```python
def classify_with_llm(email_text):
    prompt = f"""
    Categorize this email into one of:
    [applied, rejected, interview, assessment, follow_up, recruiter_outreach, unknown].
    Email: {email_text}
    """
    return call_llm(prompt)
```

---

## Example Extraction Logic

```python
def extract_entities(email_text):
    # Basic regex or NER (spaCy)
    company = extract_company(email_text)
    job_title = extract_job_title(email_text)
    job_id = extract_job_id(email_text)
    recruiter = extract_recruiter(email_text)
    return {
        "company": company,
        "job_title": job_title,
        "job_id": job_id,
        "recruiter": recruiter,
    }
```

---

## Security & Compliance Considerations

- Use OAuth 2.0 with refresh tokens (never store passwords).
- Encrypt tokens at rest.
- Log minimal email content (PII handling).
- Allow user to revoke Graph permissions anytime.

---

## Suggested Tech Stack

- **Backend:** Python (FastAPI)
- **Graph API:** `msal`, `requests`
- **Email parsing:** `beautifulsoup4` for HTML → text
- **NLP:** spaCy, or OpenAI GPT / Azure OpenAI
- **Database:** PostgreSQL (prod), SQLite (local)
- **Scheduling:** Celery beat or cron

---

## Optional Starter Code (Graph Ingestion)

```python
import msal
import requests

GRAPH_API = "https://graph.microsoft.com/v1.0"

app = msal.PublicClientApplication(
    client_id=CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
)

result = app.acquire_token_by_username_password(
    username=USERNAME,
    password=PASSWORD,
    scopes=["Mail.Read"],
)

headers = {"Authorization": f"Bearer {result['access_token']}"}
resp = requests.get(f"{GRAPH_API}/me/messages", headers=headers)
print(resp.json())
```

---

## Reporting Examples (SQL)

```sql
-- All rejected applications
SELECT * FROM job_applications WHERE current_status = 'rejected';

-- Active applications
SELECT * FROM job_applications WHERE current_status IN ('applied', 'interview');

-- Applications per week
SELECT date_trunc('week', applied_date) AS week, count(*)
FROM job_applications
GROUP BY week
ORDER BY week;
```

---

## Future Enhancements

- Add a UI dashboard (Streamlit or React).
- Train a custom classifier for your email patterns.
- Integrate calendar events for interview scheduling.
- Alerting via Slack/Teams for status changes.
