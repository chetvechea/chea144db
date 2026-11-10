"""Initial Supabase licensing client. Never ship database admin keys."""

from dataclasses import dataclass
from datetime import datetime, timezone
import os
import time
from urllib.parse import urlparse

from packaging.version import Version, InvalidVersion
import requests

CURRENT_VERSION = "1.0.0"
RECHECK_SECONDS = 15 * 60


class LicensingError(Exception):
    """Safe, user-facing service/configuration failure."""


@dataclass(frozen=True)
class LicenseStatus:
    valid: bool
    reason: str
    expires_at: datetime | None
    latest_version: str
    minimum_version: str
    checked_at: float

    @property
    def update_available(self) -> bool:
        return Version(self.latest_version) > Version(CURRENT_VERSION)

    @property
    def update_required(self) -> bool:
        return Version(CURRENT_VERSION) < Version(self.minimum_version)

    @property
    def allowed(self) -> bool:
        return (
            self.valid and not self.update_required
            and self.expires_at is not None
            and datetime.now(timezone.utc) < self.expires_at
            and time.monotonic() - self.checked_at < RECHECK_SECONDS
        )


def verify_license(license_key: str) -> LicenseStatus:
    """Call only from a background thread/worker, not a Streamlit render path."""
    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    public_key = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    parsed = urlparse(base)
    if parsed.scheme != "https" or not parsed.hostname or not public_key:
        raise LicensingError("Set SUPABASE_URL (HTTPS) and SUPABASE_PUBLISHABLE_KEY first.")
    if not public_key.startswith("sb_publishable_"):
        raise LicensingError("Use a Supabase publishable key, never a secret/service-role key.")
    if not 20 <= len(license_key) <= 200:
        raise LicensingError("The license key must contain between 20 and 200 characters.")
    try:
        response = requests.post(
            f"{base}/rest/v1/rpc/check_license",
            headers={"apikey": public_key},
            json={"submitted_key": license_key}, timeout=(5, 10),
            allow_redirects=False,
        )
        if response.status_code != 200:
            raise LicensingError(f"License service returned HTTP {response.status_code}. Check backend setup or try again.")
        data = response.json()
        if type(data["valid"]) is not bool or data["reason"] not in {"active", "invalid", "revoked", "expired"}:
            raise ValueError("Invalid license fields")
        expires = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00")) if data["expires_at"] else None
        latest, minimum = str(data["latest_version"]), str(data["minimum_version"])
        if Version(minimum) > Version(latest):
            raise ValueError("Minimum version exceeds latest")
        if expires is not None and expires.tzinfo is None:
            raise ValueError("Expiry requires timezone")
        if data["valid"] and (expires is None or data["reason"] != "active"):
            raise ValueError("Incomplete active license")
        return LicenseStatus(data["valid"], data["reason"], expires, latest, minimum, time.monotonic())
    except requests.Timeout as exc:
        raise LicensingError("License server timed out. Check your connection and retry.") from exc
    except requests.RequestException as exc:
        raise LicensingError("Cannot connect securely to the license server. Check your network and Supabase project status.") from exc
    except (ValueError, KeyError, TypeError, InvalidVersion) as exc:
        raise LicensingError("License server returned an invalid response. Contact the administrator.") from exc


def credential_store():
    """Explicit Windows backend: do not silently fall back to a plaintext file."""
    from keyring.backends.Windows import WinVaultKeyring
    return WinVaultKeyring()


def load_saved_key() -> str | None:
    return credential_store().get_password("SocialPoster.Licensing", "license")


def save_key(key: str) -> None:
    credential_store().set_password("SocialPoster.Licensing", "license", key)
