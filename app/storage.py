import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class JobApplication:
    company_name: Optional[str]
    job_title: Optional[str]
    job_id: Optional[str]
    recruiter_name: Optional[str]
    applied_date: Optional[str]
    current_status: str


class Storage:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    job_title TEXT,
                    job_id TEXT,
                    recruiter_name TEXT,
                    applied_date TEXT,
                    current_status TEXT NOT NULL,
                    last_email_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS emails (
                    id TEXT PRIMARY KEY,
                    subject TEXT,
                    sender TEXT,
                    received_at TEXT,
                    body_text TEXT,
                    classification TEXT,
                    confidence REAL,
                    job_application_id INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(job_application_id) REFERENCES job_applications(id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_application_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    source_email_id TEXT,
                    changed_at TEXT NOT NULL,
                    FOREIGN KEY(job_application_id) REFERENCES job_applications(id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sync_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    delta_link TEXT
                )
                """
            )
            conn.commit()

    def get_delta_link(self) -> Optional[str]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT delta_link FROM sync_state WHERE id = 1")
            row = cursor.fetchone()
            return row[0] if row else None

    def set_delta_link(self, delta_link: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO sync_state (id, delta_link) VALUES (1, ?)",
                (delta_link,),
            )
            conn.commit()

    def upsert_job(self, job: JobApplication, email_id: str) -> int:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id FROM job_applications
                WHERE job_id IS ?
                  AND company_name IS ?
                  AND job_title IS ?
                """,
                (job.job_id, job.company_name, job.job_title),
            )
            row = cursor.fetchone()
            if row:
                job_id = row[0]
                cursor.execute(
                    """
                    UPDATE job_applications
                    SET recruiter_name = COALESCE(?, recruiter_name),
                        current_status = ?,
                        last_email_id = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        job.recruiter_name,
                        job.current_status,
                        email_id,
                        now,
                        job_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO job_applications (
                        company_name,
                        job_title,
                        job_id,
                        recruiter_name,
                        applied_date,
                        current_status,
                        last_email_id,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job.company_name,
                        job.job_title,
                        job.job_id,
                        job.recruiter_name,
                        job.applied_date,
                        job.current_status,
                        email_id,
                        now,
                        now,
                    ),
                )
                job_id = cursor.lastrowid
            conn.commit()
            return job_id

    def insert_email(
        self,
        email_id: str,
        subject: str,
        sender: str,
        received_at: str,
        body_text: str,
        classification: str,
        confidence: float,
        job_application_id: Optional[int],
    ) -> None:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO emails (
                    id,
                    subject,
                    sender,
                    received_at,
                    body_text,
                    classification,
                    confidence,
                    job_application_id,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email_id,
                    subject,
                    sender,
                    received_at,
                    body_text,
                    classification,
                    confidence,
                    job_application_id,
                    now,
                ),
            )
            conn.commit()

    def insert_status_history(
        self,
        job_application_id: int,
        status: str,
        source_email_id: str,
    ) -> None:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO status_history (
                    job_application_id,
                    status,
                    source_email_id,
                    changed_at
                ) VALUES (?, ?, ?, ?)
                """,
                (job_application_id, status, source_email_id, now),
            )
            conn.commit()
