"""Streamlit entry point. Launch with python -m streamlit run app.py."""

from importlib.metadata import version
import platform

import streamlit as st

from social_poster import __version__
from social_poster.config import load_settings
from social_poster.logging_setup import configure_logging


def main() -> None:
    st.set_page_config(page_title="Social Media Auto Post Tool", page_icon="🎬", layout="wide")
    try:
        settings = load_settings()
        settings.ensure_directories()
        logger = configure_logging(settings)
    except (OSError, ValueError) as error:
        st.error(f"Startup failed: {error}")
        st.stop()

    st.title(settings.app_name)
    st.caption(f"Version {__version__} · Local Windows application")
    st.success("Task 1 foundation is ready.")
    st.write(
        "Your workspace is set up. Facebook Page Reels will be the first publishing "
        "feature, followed by YouTube Shorts and TikTok videos."
    )
    st.info(
        "This starter does not sign in, upload media, or publish posts. "
        "Account management and the posting queue will arrive in later tasks."
    )

    st.subheader("Environment")
    st.table([
        {"Component": "Python", "Version": platform.python_version()},
        {"Component": "Streamlit", "Version": version("streamlit")},
        {"Component": "Playwright", "Version": version("playwright")},
    ])
    with st.expander("Local storage"):
        st.json({
            "Project": str(settings.project_root),
            "Database (reserved for Task 2)": str(settings.database_path),
            "Browser profiles": str(settings.profiles_dir),
            "Staged media": str(settings.media_dir),
            "Diagnostics": str(settings.artifacts_dir),
            "Logs": str(settings.log_dir),
        })
    if st.button("Write a test log entry"):
        logger.info("User requested a foundation logging check")
        st.success(f"Test entry written to {settings.log_dir / 'app.log'}")


if __name__ == "__main__":
    main()
