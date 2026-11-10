# Social Media Auto Post Tool

## Windows executable

Build with `scripts\build-exe.ps1`. The output is `dist\SocialPostTool.exe`.
Double-click it to open the current foundation app in your default browser.
No separate Python installation is required on the destination Windows x64 PC.
Keep the launcher console open; Ctrl+C or closing it stops the local server.
Closing only the browser tab does not stop the app.

The executable stores runtime data under `%LOCALAPPDATA%\SocialPoster`, outside
its temporary extraction directory. It binds only to localhost and chooses an
available port. The first launch may take a little time to extract dependencies.

To open the separate licensing preview, run `SocialPostTool.exe --license` with
the Supabase environment settings from LICENSING.md. The default foundation app
does not enforce licensing yet. No cloud secrets, saved profiles, or personal
runtime data are included. Publishing is not implemented, and Playwright browser
binaries are not included in this foundation build. This is a portable executable,
not an installation wizard or a signed production release.

Licensing/update architecture, cloud SQL setup, and the separate initial setup
screen are documented in [LICENSING.md](LICENSING.md). Start the guided helper
with `scripts\setup-license.ps1` after creating the Supabase backend.

Task 1 foundation: Python package layout, Streamlit starter, configuration,
rotating application logs, and Windows setup scripts. Publishing, SQLite tables,
accounts, and the worker are intentionally reserved for later tasks.

## Requirements

- Windows with Python 3.11–3.14 and pip available as `python`.
- Internet access for the initial dependencies and Playwright Chromium download.

## Setup and run (PowerShell)

```powershell
Set-Location 'E:\Post Tool'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://127.0.0.1:8501. Stop the server with Ctrl+C. On subsequent runs,
only the final command is needed. No virtual-environment activation is required.

Alternatively, run ` .\scripts\setup.ps1 ` once, then ` .\scripts\run.ps1 `.
If PowerShell blocks scripts, use the explicit Python commands above; no execution
policy change is necessary. The scripts resolve the project directory themselves.

Optional activation (only if your PowerShell policy permits it):

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
# When finished:
deactivate
```

## Implementation rules for subsequent tasks

- All application Playwright launches will explicitly use `headless=False`, so
  manual login and publishing automation are visible.
- Browser and platform automation remain separate from Streamlit UI code.
- Targeted try/except blocks will capture the failed automation step and its
  concrete failure reason. The UI will display these using `st.error` or `st.toast`.
- Background workers will report errors to the UI through job results, without
  calling Streamlit directly. Diagnostic logs must not expose session credentials.
- Browser resources must be released on failure. Uncertain publishing outcomes
  require verification instead of automatic reposting.

These rules are also recorded in `AGENTS.md` for future implementation work.
Task 1 has no application Playwright launch yet; its startup errors already use
`st.error`.

### Long-running automation and upload policy

Task 1 defines `AutomationSettings` in `src/social_poster/config.py`:

| Setting | Default |
| --- | --- |
| Browser headless mode | `False` |
| Ordinary action timeout | 30 seconds |
| File attachment and upload-completion timeout | 5 minutes |
| Final publication-confirmation timeout | 5 minutes |
| Random pacing between clicks | 1–3 seconds |

The publishing worker will run in a separate process. Streamlit will submit jobs
and poll persisted progress, keeping the UI responsive during uploads. Browser
objects stay in that worker, and UI reruns must not create duplicate workers.
The worker and its SQLite queue are implemented in later tasks; these settings
do not start automation in Task 1.

Platform adapters will prefer scoped role, label, and text locators over dynamic
CSS classes. They must explicitly apply the longer timeouts both to attaching
files and to observing upload completion, then separately to publication
confirmation. Random pacing runs only in the worker and supplements readiness
checks; it cannot guarantee that automation will not be flagged. A timeout after
submitting a post requires verification, without automatic reposting.

## Manual acceptance check

1. Confirm the page displays **Task 1 foundation is ready** and dependency versions.
2. Expand **Local storage** and confirm the paths point to this project.
3. Click **Write a test log entry** and inspect `logs\app.log`.
4. Refresh the page; the application should still work without duplicate log handlers.
5. Stop and restart the server using the same command.

The app creates `data\profiles`, `data\media`, `data\artifacts`, and `logs`.
`data\app.db` is only a reserved path; no database is created in Task 1.
Chromium is installed for the upcoming automation tasks; the starter does not
open a browser automation session or access Facebook.

## Configuration

Optional environment variables, set before launching:

| Variable | Default | Purpose |
| --- | --- | --- |
| `SOCIAL_POSTER_DATA_DIR` | `data` | Runtime data root |
| `SOCIAL_POSTER_LOG_DIR` | `logs` | Log directory |
| `SOCIAL_POSTER_LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR, CRITICAL |

Relative paths resolve against the project root. Environment variables are read
directly; `.env` files are not automatically loaded. Logs rotate at 5 MiB with
three backups. The application binds to loopback only; no remote access is configured.
Runtime data and future browser sessions are excluded from Git. Git exclusion is
not encryption; keep browser profiles private because they can contain login sessions.

## Architecture

- `app.py`: Streamlit entry point.
- `src/social_poster/config.py`: immutable settings and runtime paths.
- `src/social_poster/logging_setup.py`: application logging.
- `src/social_poster/{ui,services,database,browser,platforms,queue,media}`:
  reserved module boundaries for subsequent tasks.
- `scripts/`: Windows setup and launch helpers.
- `tests/`: reserved for meaningful behavior tests as features are implemented.

`requirements.txt` installs the editable local package and its dependencies from
`pyproject.toml`, keeping a single dependency declaration. `requirements-lock.txt`, when present,
records the versions verified in this workspace. To recreate that environment,
install it with `python -m pip install -r requirements-lock.txt` before `pip install -e .`.

Installation references: [Streamlit](https://docs.streamlit.io/get-started/installation/command-line)
and [Playwright](https://playwright.dev/python/docs/library).
