"""Tests for X and LinkedIn posters."""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.linkedin_poster import LinkedInPoster
from src.x_poster import XPoster


class TestXPoster:
    def test_not_configured_without_env(self):
        with patch.dict(os.environ, {}, clear=True):
            poster = XPoster()
            assert not poster.is_configured

    def test_configured_with_env(self):
        env = {
            "X_API_KEY": "test_key",
            "X_API_SECRET": "test_secret",
            "X_ACCESS_TOKEN": "test_token",
            "X_ACCESS_SECRET": "test_access",
            "X_BEARER_TOKEN": "test_bearer",
        }
        with patch.dict(os.environ, env, clear=True):
            poster = XPoster()
            assert poster.is_configured

    def test_post_raises_when_not_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            poster = XPoster()
            with pytest.raises(RuntimeError, match="not configured"):
                poster.post("test tweet")

    def test_post_success(self):
        env = {
            "X_API_KEY": "test_key",
            "X_API_SECRET": "test_secret",
            "X_ACCESS_TOKEN": "test_token",
            "X_ACCESS_SECRET": "test_access",
            "X_BEARER_TOKEN": "test_bearer",
        }
        with patch.dict(os.environ, env, clear=True):
            poster = XPoster()
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'{"data":{"id":"123","text":"test"}}'
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)

            with patch("urllib.request.urlopen", return_value=mock_resp):
                result = poster.post("test tweet")
                assert result["data"]["id"] == "123"


class TestLinkedInPoster:
    def test_not_configured_without_env(self):
        with patch.dict(os.environ, {}, clear=True):
            poster = LinkedInPoster()
            assert not poster.is_configured

    def test_configured_with_env(self):
        env = {
            "LINKEDIN_CLIENT_ID": "test_id",
            "LINKEDIN_CLIENT_SECRET": "test_secret",
            "LINKEDIN_ACCESS_TOKEN": "test_token",
        }
        with patch.dict(os.environ, env, clear=True):
            poster = LinkedInPoster()
            assert poster.is_configured

    def test_post_raises_when_not_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            poster = LinkedInPoster()
            with pytest.raises(RuntimeError, match="not configured"):
                poster.post("test post")

    def test_post_success(self):
        env = {
            "LINKEDIN_CLIENT_ID": "test_id",
            "LINKEDIN_CLIENT_SECRET": "test_secret",
            "LINKEDIN_ACCESS_TOKEN": "test_token",
        }
        with patch.dict(os.environ, env, clear=True):
            poster = LinkedInPoster()
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'{"id":"urn:li:share:123"}'
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)

            with patch("urllib.request.urlopen", return_value=mock_resp):
                result = poster.post("test post")
                assert "id" in result
