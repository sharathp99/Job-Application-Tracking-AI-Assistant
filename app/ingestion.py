from datetime import datetime
from typing import Dict, List

from bs4 import BeautifulSoup

from app.classifier import classify
from app.extractor import extract_entities
from app.graph_client import GraphClient
from app.storage import JobApplication, Storage


def normalize_body(body: Dict) -> str:
    content = body.get("content", "")
    content_type = body.get("contentType", "text").lower()
    if content_type == "html":
        soup = BeautifulSoup(content, "html.parser")
        return soup.get_text(" ", strip=True)
    return content.strip()


def normalize_sender(sender_data: Dict) -> str:
    email_address = sender_data.get("emailAddress") or {}
    name = email_address.get("name", "")
    address = email_address.get("address", "")
    if name and address:
        return f"{name} <{address}>"
    return address or name


def process_messages(
    messages: List[Dict],
    storage: Storage,
) -> None:
    for message in messages:
        message_id = message.get("id")
        subject = message.get("subject", "")
        received_at = message.get("receivedDateTime", "")
        sender = normalize_sender(message.get("from", {}))
        body_text = normalize_body(message.get("body", {}))

        classification = classify(subject, body_text)
        extraction = extract_entities(subject, body_text)

        applied_date = None
        if received_at:
            applied_date = datetime.fromisoformat(received_at.replace("Z", "+00:00")).date().isoformat()

        job = JobApplication(
            company_name=extraction.company,
            job_title=extraction.job_title,
            job_id=extraction.job_id,
            recruiter_name=extraction.recruiter,
            applied_date=applied_date,
            current_status=classification.label,
        )

        job_application_id = storage.upsert_job(job, message_id)
        storage.insert_email(
            email_id=message_id,
            subject=subject,
            sender=sender,
            received_at=received_at,
            body_text=body_text,
            classification=classification.label,
            confidence=classification.confidence,
            job_application_id=job_application_id,
        )
        storage.insert_status_history(
            job_application_id=job_application_id,
            status=classification.label,
            source_email_id=message_id,
        )


def ingest_mailbox(
    graph_client: GraphClient,
    storage: Storage,
    mailbox_user: str,
    access_token: str,
) -> None:
    delta_link = storage.get_delta_link()
    response = graph_client.list_messages_delta(
        mailbox_user=mailbox_user,
        access_token=access_token,
        delta_link=delta_link,
    )

    while True:
        messages = response.get("value", [])
        if messages:
            process_messages(messages, storage)

        delta_link = response.get("@odata.deltaLink")
        next_link = response.get("@odata.nextLink")
        if delta_link:
            storage.set_delta_link(delta_link)
            break
        if not next_link:
            break
        response = graph_client.list_messages_delta(
            mailbox_user=mailbox_user,
            access_token=access_token,
            delta_link=next_link,
        )
