import re
from dataclasses import dataclass
from typing import Optional


COMPANY_REGEX = re.compile(r"(?:at|with)\s+([A-Z][A-Za-z0-9&\-\s]{2,})")
JOB_ID_REGEX = re.compile(r"(?:Job|Req|Requisition)\s*#?\s*([A-Z0-9-]{4,})")
ROLE_REGEX = re.compile(r"(?:role|position|title)\s*[:\-]\s*([A-Za-z0-9\-\s/]{3,})")
RECRUITER_REGEX = re.compile(r"(?:Regards|Thanks|Sincerely|Best),\s*([A-Z][A-Za-z\s]+)")


@dataclass(frozen=True)
class ExtractionResult:
    company: Optional[str]
    job_title: Optional[str]
    job_id: Optional[str]
    recruiter: Optional[str]


def _search(pattern: re.Pattern, text: str) -> Optional[str]:
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return None


def extract_entities(subject: str, body: str) -> ExtractionResult:
    text = f"{subject}\n{body}"
    company = _search(COMPANY_REGEX, text)
    job_title = _search(ROLE_REGEX, text)
    job_id = _search(JOB_ID_REGEX, text)
    recruiter = _search(RECRUITER_REGEX, text)
    return ExtractionResult(
        company=company,
        job_title=job_title,
        job_id=job_id,
        recruiter=recruiter,
    )
