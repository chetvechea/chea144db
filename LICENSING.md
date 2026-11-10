# Licensing and live update architecture

## 1. Cloud and trust boundary

Use Supabase PostgreSQL for licenses and a singleton release record. The initial
implementation uses a narrowly scoped SQL RPC instead of shipping admin database
credentials or adding another server. RLS is enabled, direct client table access
is revoked, and only the verification RPC is public. Admin operations run in the
Supabase SQL editor. For production, place verification behind an Edge Function
with server-side rate limiting and monitoring before broadly distributing keys.

Supabase Free is suitable for a pilot, but projects may pause after low activity.
This online-required policy blocks access during outages; choose paid availability
or design signed offline leases before promising offline use.

## 2. Admin setup and key lifecycle

1. Create a Supabase project and run `cloud/licensing.sql` once in its SQL editor.
2. Enable/use its Data API. Copy the project URL and **publishable** API key.
   Never distribute secret keys, service-role keys, or database passwords.
3. Issue a calendar-month license with `select * from public.issue_license(1);`
   or a calendar-year license with `select * from public.issue_license(12);`.
   Validity begins at issuance, in UTC. Copy the random key for the customer;
   the database stores only a SHA-256 hash. Keep the returned license ID for admin work.
4. Revoke using the SQL editor (replace the UUID):

```sql
update public.app_licenses set revoked = true where id = 'LICENSE-UUID';
```

Keys are bearer credentials in this initial version. Device limits, customer
authentication, transfers, and a graphical admin panel are not implemented.

## 3. Local activation and periodic verification

The user enters a key once. After successful verification it is saved in Windows
Credential Manager, not a plaintext JSON file or a `valid=true` flag. Each app
startup verifies online again. Successful results are held in memory for at most
15 minutes, and never beyond license expiration. The UI polls a background
network future every two seconds; it does not perform the HTTP request itself.
Network failures block access after the current verification window expires;
an explicit invalid/expired/revoked result blocks immediately. In this initial
screen failed rechecks clear access immediately and retry at the next interval
or when the user clicks recheck.

Use `LicenseStatus.allowed` at the actual submission boundary and reverify before
the future worker starts a publishing job. Do not rely only on a UI banner.
Do not interrupt a publish click mid-flight, since its outcome may be uncertain.
The existing Task 1 `app.py` is not gated by this demonstration screen yet.

## 4. Update policy

`CURRENT_VERSION = "1.0.0"` is in the licensing client. Release comparison uses
`packaging.version.Version`, so 1.10.0 correctly sorts after 1.9.0. The existing
foundation package is still 0.1.0; align its version with CURRENT_VERSION when
cutting the first distributed release.

Publish a normal update:

```sql
update public.app_release set latest_version = '1.1.0' where id = 1;
```

Require an update for vulnerable/unsupported versions:

```sql
update public.app_release
set latest_version = '1.2.0', minimum_version = '1.2.0' where id = 1;
```

Minimum supported version expresses critical updates more precisely than a
global boolean. New release metadata arrives on startup and every 15 minutes,
or via manual recheck. This is polling, not an instant push notification.
The code notifies or denies access; it does not download or install executables.

## 5. Run the setup screen

```powershell
Set-Location 'E:\Post Tool'
python -m venv .venv # Only if the environment does not exist yet
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:SUPABASE_URL = 'https://YOUR-PROJECT.supabase.co'
$env:SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_YOUR-PUBLIC-KEY'
.\.venv\Scripts\python.exe -m streamlit run license_setup.py
```

Alternatively run `scripts\setup-license.ps1`, which installs dependencies,
prompts for the two public settings, and opens the setup screen. Environment
settings apply to that process; rerunning the helper prompts again. The customer
license is retained in Windows Credential Manager. A distribution build should
include the fixed public project settings in its configuration, not ask customers
to set up Supabase. This helper is not a Windows executable installer.

## 6. Validation and distribution checklist

- Test active, expired, revoked, invalid, and saved-key restart flows against your project.
- Test unavailable network, malformed cloud responses, and critical updates.
- Confirm anonymous table reads and calls to `issue_license` are denied.
- Add rate limiting, access logging without raw keys, and device limits if desired.
- Integrate the gate into both the UI and publishing worker before distribution.
- A local Python app can be modified by its owner; this is licensing enforcement
  for normal use, not tamper-proof DRM. Persisted signed offline leases and a
  signed installer/updater require additional implementation.

No Supabase project has been created or deployed by this change. The SQL and
client must be tested together against your own project before distribution.
