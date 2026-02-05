import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    tenant_id: str
    client_id: str
    mailbox_user: str
    db_path: str



def get_settings() -> Settings:
    tenant_id = os.getenv("TENANT_ID", "").strip()
    client_id = os.getenv("CLIENT_ID", "").strip()
    mailbox_user = os.getenv("MAILBOX_USER", "me").strip()
    db_path = os.getenv("DB_PATH", "job_tracker.db").strip()

    if not tenant_id or not client_id:
        raise ValueError(
            "TENANT_ID and CLIENT_ID must be set in environment or .env file"
        )

    return Settings(
        tenant_id=tenant_id,
        client_id=client_id,
        mailbox_user=mailbox_user,
        db_path=db_path,
    )
