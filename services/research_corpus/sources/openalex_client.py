from typing import Any

import requests


class OpenAlexClient:
    """HTTP client for the OpenAlex REST API."""

    BASE_URL = "https://api.openalex.org"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def search_works(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> tuple[dict[str, Any], ...]:
        if not query.strip():
            raise ValueError("query must not be empty")

        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

        params: dict[str, Any] = {
            "search": query,
            "per_page": limit,
        }

        if self.api_key:
            params["api_key"] = self.api_key

        response = requests.get(
            f"{self.BASE_URL}/works",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        payload = response.json()

        return tuple(payload.get("results", ()))

    def get_work(
        self,
        work_id: str,
    ) -> dict[str, Any] | None:
        if not work_id.strip():
            raise ValueError("work_id must not be empty")

        params: dict[str, Any] = {}

        if self.api_key:
            params["api_key"] = self.api_key

        response = requests.get(
            f"{self.BASE_URL}/works/{work_id}",
            params=params,
            timeout=self.timeout,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return response.json()