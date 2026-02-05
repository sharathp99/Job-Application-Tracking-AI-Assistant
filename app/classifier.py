from dataclasses import dataclass
from typing import Dict, Tuple


RULES: Dict[str, Tuple[str, ...]] = {
    "rejected": (
        "we regret",
        "unfortunately",
        "not moving forward",
        "position has been filled",
    ),
    "interview": (
        "schedule",
        "interview",
        "phone screen",
        "meeting invite",
    ),
    "assessment": (
        "assessment",
        "coding challenge",
        "technical test",
        "take-home",
    ),
    "applied": (
        "application received",
        "thank you for applying",
        "we received your application",
    ),
    "follow_up": (
        "following up",
        "checking in",
        "any update",
    ),
    "recruiter_outreach": (
        "your background",
        "opportunity",
        "reach out",
        "open role",
    ),
}


@dataclass(frozen=True)
class ClassificationResult:
    label: str
    confidence: float
    method: str


def classify(subject: str, body: str) -> ClassificationResult:
    text = f"{subject} {body}".lower()
    for label, keywords in RULES.items():
        if any(keyword in text for keyword in keywords):
            return ClassificationResult(label=label, confidence=0.85, method="rules")
    return ClassificationResult(label="unknown", confidence=0.2, method="rules")
