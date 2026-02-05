# Job-Application-Tracking-AI-Assistant

## Overview

This repository provides a starter implementation for a job application tracking agent that ingests Outlook emails, classifies them, extracts structured data, and stores job application history in SQLite.

## Setup

1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Fill in `TENANT_ID` and `CLIENT_ID` from your Azure app registration.

## Run the ingestion pipeline

```bash
python -m app.main
```

The device code flow will prompt you to authenticate in a browser. Once complete, the pipeline will:

- Pull Outlook inbox messages via the Microsoft Graph delta endpoint.
- Classify the email into a job status.
- Extract company/job details.
- Store records in `job_tracker.db` (or the path set in `DB_PATH`).

## Project Structure

```
app/
  classifier.py   # Rule-based email classification
  extractor.py    # Regex-based entity extraction
  graph_client.py # Microsoft Graph API client
  ingestion.py    # Normalization + pipeline orchestration
  storage.py      # SQLite storage layer
  main.py         # CLI entrypoint
```

## Next Steps

- Expand the classifier with an LLM fallback.
- Add a UI/dashboard for browsing applications.
- Improve extraction accuracy using spaCy or custom NER.
