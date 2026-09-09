"""X / Twitter poster using OAuth 1.0a via requests."""

from __future__ import annotations

import os
from typing import Any

import requests
from requests_oauthlib import OAuth1


class XPoster:
    """Post to X using OAuth 1.0a via requests."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("X_API_KEY", "")
        self.api_secret = os.environ.get("X_API_SECRET", "")
        self.access_token = os.environ.get("X_ACCESS_TOKEN", "")
        self.access_secret = os.environ.get("X_ACCESS_SECRET", "")
        self.session = requests.Session()

    @property
    def is_configured(self) -> bool:
        return bool(
            self.api_key and self.api_secret and self.access_token and self.access_secret
        )

    def _get_oauth(self) -> OAuth1:
        """Get OAuth 1.0a authentication."""
        return OAuth1(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_secret,
            signature_method="HMAC-SHA1",
        )

    def post(self, text: str) -> dict[str, Any]:
        """Post a tweet."""
        if not self.is_configured:
            raise RuntimeError("X API credentials not configured")

        url = "https://api.twitter.com/2/tweets"
        payload = {"text": text}
        auth = self._get_oauth()

        resp = self.session.post(url, json=payload, auth=auth, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_me(self) -> dict[str, Any]:
        """Get current user info."""
        if not self.is_configured:
            raise RuntimeError("X API credentials not configured")

        url = "https://api.twitter.com/2/users/me"
        auth = self._get_oauth()

        resp = self.session.get(url, auth=auth, timeout=30)
        resp.raise_for_status()
        return resp.json()
