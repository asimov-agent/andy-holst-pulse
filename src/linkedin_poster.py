"""LinkedIn poster using the LinkedIn API."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class LinkedInPoster:
    """Post to LinkedIn using the LinkedIn Share API."""

    def __init__(self) -> None:
        self.client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")
        self.client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
        self.access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.access_token)

    def post(self, text: str) -> dict[str, Any]:
        """Post a share to LinkedIn."""
        if not self.is_configured:
            raise RuntimeError("LinkedIn API credentials not configured")

        url = "https://api.linkedin.com/v2/ugcPosts"
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

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"LinkedIn API error {e.code}: {body}") from e
