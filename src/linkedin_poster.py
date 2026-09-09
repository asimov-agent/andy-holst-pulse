"""LinkedIn poster using the LinkedIn Share API."""

from __future__ import annotations

import os
from typing import Any

import requests


class LinkedInPoster:
    """Post to LinkedIn using the LinkedIn Share API via requests."""

    def __init__(self) -> None:
        self.access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
        self.session = requests.Session()

    @property
    def is_configured(self) -> bool:
        return bool(self.access_token)

    def post(self, text: str) -> dict[str, Any]:
        """Post a share to LinkedIn."""
        if not self.is_configured:
            raise RuntimeError("LinkedIn API credentials not configured")

        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        payload = {
            "author": "urn:li:person:me",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        resp = self.session.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
