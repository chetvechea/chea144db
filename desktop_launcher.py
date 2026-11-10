"""Frozen desktop entry point; console provides a visible shutdown control."""
import os
from pathlib import Path
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

from streamlit.web import cli


def main():
    bundle = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    root = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "SocialPoster"
    root.mkdir(parents=True, exist_ok=True)
    os.chdir(root)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    no_browser = "--no-browser" in sys.argv
    script = "license_setup.py" if "--license" in sys.argv else "app.py"

    def open_when_ready():
        for _ in range(120):
            try:
                with urllib.request.urlopen(url + "/_stcore/health", timeout=1) as response:
                    if response.status == 200:
                        if not no_browser:
                            webbrowser.open(url)
                        return
            except OSError:
                time.sleep(0.5)

    threading.Thread(target=open_when_ready, daemon=True).start()
    print(f"Social Media Auto Post Tool: {url}", flush=True)
    print("Keep this window open. Press Ctrl+C or close it to stop the app.", flush=True)
    sys.argv = ["streamlit", "run", str(bundle / script),
                "--server.address=127.0.0.1", f"--server.port={port}",
                "--server.headless=true", "--server.fileWatcherType=none",
                "--global.developmentMode=false", "--browser.gatherUsageStats=false",
                "--server.maxUploadSize=1024"]
    # Streamlit headless disables its own browser opener, not Playwright's browser.
    cli.main()


if __name__ == "__main__":
    main()
