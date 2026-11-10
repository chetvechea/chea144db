# Project implementation rules

- Use Python, Streamlit for UI, Playwright for all platform automation, and SQLite for persistence.
- Implement only the task currently authorized by the user; wait for their test confirmation before advancing.
- Launch every application Playwright browser or persistent context with explicit `headless=False`. Manual login and publishing must remain visible.
- Run long-lived Playwright operations in a separate worker process, never in Streamlit's script thread. Submit jobs and poll persisted progress from the UI without blocking joins, subprocess.run, or asyncio.run around publishing. Launch Windows background workers with hidden console windows while keeping the browser visible. Enforce a single worker and profile ownership across UI reruns.
- Prefer scoped get_by_role, get_by_label, and get_by_text locators with explicit names. Avoid dynamic CSS classes and ambiguous first-match fallbacks. Keep platform-specific locators in the platform adapter and use observable readiness conditions.
- Apply randomized 1–3 second pacing between clicks inside the worker only, using shared AutomationSettings. Delays supplement readiness waits and do not guarantee avoidance of platform detection. Never sleep in the Streamlit UI thread.
- Use AutomationSettings.upload_timeout_ms explicitly for file attachment and upload-completion waits, and publish_confirmation_timeout_ms for final publication confirmation (both default to 300000 ms). Keep ordinary action timeouts separate. A confirmation timeout is an uncertain result requiring verification, not an automatic retry.
- Keep Streamlit UI under `src/social_poster/ui`, browser lifecycle under `browser`, and platform interactions under `platforms`. Keep `app.py` as the entry point; automation modules must not import Streamlit.
- Handle expected failures with targeted try/except blocks. Include the failing step and concrete reason in errors; do not silently swallow failures or report success after a failure.
- Surface automation failures through `st.error` (persistent) or `st.toast` in the UI. Background workers must return or persist structured error information for the UI instead of calling Streamlit themselves.
- Log diagnostic tracebacks without exposing passwords, cookies, session state, or tokens in user-facing messages.
- Release browser resources in finally blocks or context managers. An uncertain publishing result must not trigger an automatic repost.
- Keep requirements.txt and Windows virtual-environment setup instructions usable. Declare application dependencies in pyproject.toml to avoid conflicting lists.
