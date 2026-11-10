"""Application-owned rotating logs; safe across Streamlit reruns."""

import logging
from logging.handlers import RotatingFileHandler
from threading import Lock

from social_poster.config import Settings

_lock = Lock()


def configure_logging(settings: Settings) -> logging.Logger:
    logger = logging.getLogger("social_poster")
    with _lock:
        logger.setLevel(settings.log_level)
        logger.propagate = False
        # Only configure our namespace, leaving Streamlit's logging untouched.
        if not logger.handlers:
            handler = RotatingFileHandler(
                settings.log_dir / "app.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s: %(message)s"
            ))
            logger.addHandler(handler)
            logger.info("Application logging initialized")
    return logger
