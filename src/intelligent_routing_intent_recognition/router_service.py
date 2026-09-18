"""Business logic: prompt the LLM, sanitize its output into the contract JSON,
retry once on malformed output, and assemble the HTTP envelope.
"""

import json
import re

from .llm_client import LlmClient
from .prompt import SYSTEM_PROMPT, build_user_message

_JSON_ARRAY_RE = re.compile(r"\[.*\]", re.DOTALL)
_REQUIRED_KEYS = {"domainNm", "domainId", "trust"}


def sanitize(raw_text: str) -> str:
    """Strip markdown fences and stray prose, keep only the JSON array substring."""
    match = _JSON_ARRAY_RE.search(raw_text)
    return match.group(0) if match else raw_text.strip()


def validate(candidate: str) -> list[dict] | None:
    """Return the parsed 2-object list if it satisfies the contract, else None."""
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list) or len(parsed) != 2:
        return None
    for item in parsed:
        if not isinstance(item, dict) or set(item.keys()) != _REQUIRED_KEYS:
            return None
        try:
            trust = float(item["trust"])
        except (TypeError, ValueError):
            return None
        if not (0.0 <= trust <= 1.0):
            return None
    return parsed


class RouterService:
    def __init__(self, llm_client: LlmClient):
        self._llm_client = llm_client

    def classify(self, question: str) -> list[dict] | None:
        """Return the validated 2-domain list, or None if still malformed after one retry."""
        for _ in range(2):
            raw = self._llm_client.complete(SYSTEM_PROMPT, build_user_message(question))
            parsed = validate(sanitize(raw))
            if parsed is not None:
                return parsed
        return None

    def route(self, question: str) -> dict:
        parsed = self.classify(question)
        data_payload = parsed if parsed is not None else []
        return {
            "respCode": "00",
            "respMsg": "success",
            "data": json.dumps(data_payload, ensure_ascii=False),
        }
