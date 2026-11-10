"""Offline contract tests: no cloud calls or saved credentials."""
import os
import time
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, Mock

import requests

from social_poster.services.licensing import LicenseStatus, LicensingError, verify_license


class LicensingTests(unittest.TestCase):
    def status(self, **changes):
        values = dict(valid=True, reason="active", expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                      latest_version="1.10.0", minimum_version="1.0.0", checked_at=time.monotonic())
        values.update(changes)
        return LicenseStatus(**values)

    def test_access_and_version_policy(self):
        self.assertTrue(self.status().allowed)
        self.assertTrue(self.status().update_available)
        self.assertFalse(self.status(minimum_version="1.1.0").allowed)
        self.assertFalse(self.status(valid=False, reason="revoked").allowed)
        self.assertFalse(self.status(checked_at=time.monotonic() - 901).allowed)
        self.assertFalse(self.status(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)).allowed)

    @patch.dict(os.environ, {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_test"})
    @patch("social_poster.services.licensing.requests.post")
    def test_response_and_failures(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = dict(valid=False, reason="revoked", expires_at=None,
                                                  latest_version="1.0.0", minimum_version="1.0.0")
        self.assertFalse(verify_license("x" * 32).allowed)
        post.return_value.json.return_value = {"valid": "true"}
        with self.assertRaises(LicensingError):
            verify_license("x" * 32)
        post.side_effect = requests.Timeout()
        with self.assertRaisesRegex(LicensingError, "timed out"):
            verify_license("x" * 32)


if __name__ == "__main__":
    unittest.main()
