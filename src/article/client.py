"""Reports a completed run to the Article backend, if configured."""
from __future__ import annotations

from typing import Optional

import requests

from article.engine import RunResult


def report_run(api_url: str, project_name: str, run_result: RunResult, api_key: Optional[str] = None) -> dict:
    payload = {"project_name": project_name, **run_result.to_dict()}
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    response = requests.post(f"{api_url.rstrip('/')}/runs", json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
