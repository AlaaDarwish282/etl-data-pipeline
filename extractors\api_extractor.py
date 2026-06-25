import httpx
import pandas as pd
from typing import Optional
from datetime import datetime


class APIExtractor:
    """
    Generic REST API extractor with pagination support, retry logic,
    and automatic response normalization to DataFrame.
    """

    def __init__(self, base_url: str, headers: dict = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout

    def _get(self, endpoint: str, params: dict = None) -> dict | list:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    def extract(self, endpoint: str, params: dict = None,
                data_key: Optional[str] = None) -> pd.DataFrame:
        """
        Extract data from a REST endpoint.
        data_key: JSON key that contains the list of records (e.g. 'results', 'data').
        """
        raw = self._get(endpoint, params)
        records = raw.get(data_key) if data_key and isinstance(raw, dict) else raw
        if not isinstance(records, list):
            records = [records]
        df = pd.json_normalize(records)
        df["_extracted_at"] = datetime.utcnow().isoformat()
        return df

    def extract_paginated(self, endpoint: str, page_param: str = "page",
                          limit_param: str = "limit", limit: int = 100,
                          max_pages: int = 50, data_key: Optional[str] = None) -> pd.DataFrame:
        """Extract all pages from a paginated API."""
        frames = []
        for page in range(1, max_pages + 1):
            params = {page_param: page, limit_param: limit}
            raw = self._get(endpoint, params)
            records = raw.get(data_key) if data_key and isinstance(raw, dict) else raw
            if not records:
                break
            frames.append(pd.json_normalize(records))
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
