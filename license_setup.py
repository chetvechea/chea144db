"""Run: python -m streamlit run license_setup.py (initial integration preview)."""

from concurrent.futures import ThreadPoolExecutor
import time

import streamlit as st

from social_poster.services.licensing import (
    CURRENT_VERSION, RECHECK_SECONDS, LicensingError,
    load_saved_key, save_key, verify_license,
)

st.set_page_config(page_title="License setup", page_icon="🔑")
st.title("License setup and update check")
st.caption(f"Current version: {CURRENT_VERSION}. This screen does not publish posts.")

if "license_executor" not in st.session_state:
    st.session_state.license_executor = ThreadPoolExecutor(max_workers=1)
    try:
        st.session_state.saved_license = load_saved_key() or ""
    except Exception:
        # Credential backend errors may contain sensitive OS details.
        st.session_state.saved_license = ""
        st.error("Windows Credential Manager could not be read. Enter your key to verify it.")
    st.session_state.license_status = None
    st.session_state.next_license_check = 0.0

with st.form("activate"):
    entered_key = st.text_input("License key", type="password")
    submitted = st.form_submit_button("Activate / recheck")

if submitted and not st.session_state.get("license_future"):
    candidate = entered_key.strip() or st.session_state.saved_license
    st.session_state.pending_license = candidate
    st.session_state.license_status = None
    st.session_state.license_future = st.session_state.license_executor.submit(verify_license, candidate)


@st.fragment(run_every=2)
def show_status():
    state = st.session_state
    future = state.get("license_future")
    if future is not None and future.done():
        state.license_future = None
        state.next_license_check = time.monotonic() + RECHECK_SECONDS
        try:
            result = future.result()
            state.license_status = result
            state.license_error = None
            if result.valid:
                state.saved_license = state.pending_license
                try:
                    save_key(state.saved_license)
                except Exception:
                    st.error("License verified, but Windows Credential Manager could not save it. You may need to enter it next time.")
        except LicensingError as exc:
            state.license_status = None
            state.license_error = str(exc)
        except Exception:
            state.license_status = None
            state.license_error = "Unexpected license-check failure. Access remains blocked; retry or contact support."
    if state.saved_license and time.monotonic() >= state.next_license_check and not state.get("license_future"):
        state.pending_license = state.saved_license
        state.license_future = state.license_executor.submit(verify_license, state.saved_license)
    if state.get("license_future"):
        st.info("Checking the license server in the background…")
    if state.get("license_error"):
        st.error(state.license_error)
    status = state.license_status
    if status:
        if status.update_required:
            st.error(f"Required update: install version {status.minimum_version} or newer. Latest: {status.latest_version}.")
        elif status.update_available:
            st.warning(f"An update is available: {status.latest_version}. Installed: {CURRENT_VERSION}.")
        if not status.valid:
            st.error(f"License is {status.reason}.")
        elif status.allowed:
            st.success(f"License active until {status.expires_at.isoformat()}.")
        else:
            st.warning("Access blocked: update required, license expired, or verification is due.")
    else:
        st.info("A verified license is required before using the distributed app.")


show_status()
