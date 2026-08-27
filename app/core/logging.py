"""Logging configuration with sensitive data redaction."""

import logging
import re
import sys

SENSITIVE_PATTERNS = [
    re.compile(r"(li_at=)[^;\s]+", re.IGNORECASE),
    re.compile(r"(JSESSIONID=)[^;\s]+", re.IGNORECASE),
    re.compile(r"(Bearer\s+)[a-zA-Z0-9_\-\.]+", re.IGNORECASE),
    re.compile(r"(csrf-token:\s*)[^\s,]+", re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """Filter that scrubs sensitive cookies and auth tokens from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(r"\1[REDACTED]", record.msg)
        return True


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configures application-wide structured logging."""
    logger = logging.getLogger("tross_api")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())

    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = setup_logging()
