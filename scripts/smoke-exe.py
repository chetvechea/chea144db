"""Developer smoke test: start the packaged app and inspect it through Chromium."""
from pathlib import Path
import re
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
log_path = root / "build" / "exe-smoke.log"
with log_path.open("w", encoding="utf-8") as log:
    process = subprocess.Popen(
        [str(root / "dist" / "SocialPostTool.exe"), "--no-browser", *sys.argv[1:]],
        cwd=root, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW,
    )
    try:
        deadline = time.monotonic() + 180
        match = None
        while time.monotonic() < deadline:
            text = log_path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"Social Media Auto Post Tool: (http://127\.0\.0\.1:\d+)", text)
            if match:
                break
            if process.poll() is not None:
                raise RuntimeError(text)
            time.sleep(1)
        if not match:
            raise RuntimeError("EXE startup timed out; inspect build/exe-smoke.log")
        import urllib.request
        while time.monotonic() < deadline:
            try:
                urllib.request.urlopen(match[1] + "/_stcore/health", timeout=2).close()
                break
            except OSError:
                time.sleep(1)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            try:
                page = browser.new_page()
                page.goto(match[1])
                if "--license" in sys.argv:
                    page.get_by_role("heading", name="License setup and update check", exact=True).wait_for(timeout=60000)
                    page.get_by_role("button", name="Activate / recheck").wait_for()
                else:
                    page.get_by_text("Task 1 foundation is ready.", exact=True).wait_for(timeout=60000)
                    page.get_by_role("button", name="Write a test log entry").click()
                    page.get_by_text("Test entry written to", exact=False).wait_for()
                assert page.locator('[data-testid="stException"]').count() == 0
                print("PASS: packaged app rendered successfully", flush=True)
            finally:
                browser.close()
    finally:
        # Kill only the test process and its one-file extraction child.
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
