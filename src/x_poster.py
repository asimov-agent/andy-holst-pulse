"""X / Twitter poster."""

from __future__ import annotations

import os
from typing import Any

import urllib.request
import urllib.parse
import urllib.error
import json
import base64
import hashlib
import secrets
import time


class XPoster:
    """Post to X using OAuth 1.0a (application-only with user context)."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("X_API_KEY", "")
        self.api_secret = os.environ.get("X_API_SECRET", "")
        self.access_token = os.environ.get("X_ACCESS_TOKEN", "")
        self.access_secret = os.environ.get("X_ACCESS_SECRET", "")
        self.bearer = os.environ.get("X_BEARER_TOKEN", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret and self.access_token and self.access_secret)

    def _oauth_sign(self, method: str, url: str, params: dict[str, str]) -> str:
        """Generate OAuth 1.0a signature."""
        # Simplified OAuth 1.0a header generation
        oauth_params = {
            "oauth_consumer_key": self.api_key,
            "oauth_nonce": secrets.token_hex(16),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.access_token,
            "oauth_version": "1.0",
        }

        all_params = {**params, **oauth_params}
        sorted_params = "&".join(
            f"{urllib.parse.quote(k)}={urllib.parse.quote(all_params[k])}"
            for k in sorted(all_params.keys())
        )

        base_string = f"{method.upper()}&{urllib.parse.quote(url)}&{urllib.parse.quote(sorted_params)}"
        signing_key = f"{urllib.parse.quote(self.api_secret)}&{urllib.parse.quote(self.access_secret)}"
        signature = base64.b64encode(
            hashlib.pbkdf2_hmac('sha1', base_string.encode(), signing_key.encode(), 1)
        ).decode()

        oauth_params["oauth_signature"] = signature
        return "OAuth " + ", ".join(
            f'{urllib.parse.quote(k)}="{urllib.parse.quote(v)}"'
            for k, v in oauth_params.items()
        )

    def post(self, text: str) -> dict[str, Any]:
        """Post a tweet."""
        if not self.is_configured:
            raise RuntimeError("X API credentials not configured")

        url = "https://api.twitter.com/2/tweets"
        params = {"text": text}

        auth_header = self._oauth_sign("POST", url, params)

        req = urllib.request.Request(
            url,
            data=json.dumps(params).encode(),
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"X API error {e.code}: {body}") from e
