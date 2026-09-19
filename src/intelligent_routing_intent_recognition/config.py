"""Runtime config for the intent-routing service, read from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float = 30.0
    max_retries: int = 2


def load_config() -> Config:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")
    timeout = float(os.environ.get("DEEPSEEK_TIMEOUT", "30"))
    max_retries = int(os.environ.get("DEEPSEEK_MAX_RETRIES", "2"))
    return Config(
        api_key=api_key,
        base_url=base_url,
        model=model,
        timeout_seconds=timeout,
        max_retries=max_retries,
    )
