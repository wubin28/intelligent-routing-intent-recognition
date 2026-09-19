"""Thin wrapper around the DeepSeek chat-completions API (OpenAI-compatible)."""

import time

import requests

from .config import Config

_BACKOFF_BASE_SECONDS = 1.0


class LlmClient:
    def __init__(self, config: Config):
        self._config = config

    def complete(self, system_prompt: str, user_message: str) -> str:
        attempts = self._config.max_retries + 1
        for attempt in range(attempts):
            try:
                return self._post(system_prompt, user_message)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt == attempts - 1:
                    raise
                time.sleep(_BACKOFF_BASE_SECONDS * 2**attempt)
        raise AssertionError("unreachable")

    def _post(self, system_prompt: str, user_message: str) -> str:
        response = requests.post(
            f"{self._config.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "temperature": 0.0,
            },
            timeout=self._config.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
