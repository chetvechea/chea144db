# Source hosting and client updates

Keep application source in a private GitHub repository. Store EXE downloads as
release assets, not source commits. Private repository releases require repository
read access; for customers without GitHub access, use a separate public releases
repository (if public downloads are acceptable) or authenticated download storage.
Never put a GitHub personal access token into the desktop app.

## First upload

Connect GitHub and select the destination repository before uploading. Include
source, scripts, tests, documentation, and dependency declarations. Exclude
`.venv`, `build`, `dist`, logs, data, browser sessions, credentials, and `.env`.
`dist/SocialPostTool-source.zip` is a source-only archive prepared for this purpose;
extract its contents before using GitHub's Upload files UI, rather than committing
the ZIP itself.

## Each client release

1. Align the package/app versions with the release version, then test.
2. Build the EXE with `scripts/build-exe.ps1` and run the packaged smoke tests.
3. Create a draft GitHub release with tag `vX.Y.Z` and attach `SocialPostTool.exe`.
4. Verify downloads and publish the release before updating Supabase metadata.
5. Update `app_release.latest_version`; raise `minimum_version` only for a required
   update. The current licensing preview polls every 15 minutes.

The current EXE does not automatically replace itself. Source upload does not
update installed EXEs. The next implementation must integrate the licensing/update
gate into the main app, expose a validated download URL, and offer an update action.
Silent installation additionally requires a separate updater, verified/signed
artifacts, safe process shutdown, atomic replacement, and rollback handling.

The existing app remains a foundation preview, not a finished posting product.
