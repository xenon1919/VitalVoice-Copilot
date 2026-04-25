from __future__ import annotations

from dataclasses import dataclass


URGENT_KEYWORDS = {
    "chest pain",
    "severe shortness of breath",
    "trouble breathing",
    "fainting",
    "stroke",
    "slurred speech",
    "one-sided weakness",
    "seizure",
    "vomiting blood",
    "suicidal",
}

SAFETY_DISCLAIMER = (
    "This is general advice and not a medical diagnosis. "
    "If symptoms are severe, persistent, or worsening, consult a qualified doctor."
)

EMERGENCY_MESSAGE = (
    "Your symptoms may require urgent medical attention. "
    "Please contact emergency services or go to the nearest emergency department immediately."
)


@dataclass
class SafetyAssessment:
    urgent: bool
    reasons: list[str]


class SafetyGuard:
    def assess(self, text: str) -> SafetyAssessment:
        lower = text.lower()
        reasons = [kw for kw in URGENT_KEYWORDS if kw in lower]
        return SafetyAssessment(urgent=bool(reasons), reasons=reasons)

    def apply(self, response_text: str, urgent: bool) -> str:
        if urgent:
            return f"{EMERGENCY_MESSAGE}\n\n{SAFETY_DISCLAIMER}"
        if SAFETY_DISCLAIMER.lower() in response_text.lower():
            return response_text
        return f"{response_text.strip()}\n\n{SAFETY_DISCLAIMER}"
