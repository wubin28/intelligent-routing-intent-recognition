"""Thin wrapper around the DeepSeek chat-completions API (OpenAI-compatible)."""

import requests

from .config import Config


class LlmClient:
    def __init__(self, config: Config):
        self._config = config

    def complete(self, system_prompt: str, user_message: str) -> str:
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
