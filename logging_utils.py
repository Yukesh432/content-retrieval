import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

def get_logger(name: str = "bookchunker") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    h = logging.StreamHandler()
    h.setLevel(logging.INFO)
    fmt = logging.Formatter("%(message)s")
    h.setFormatter(fmt)
    logger.addHandler(h)
    return logger

def log_event(logger: logging.Logger, event: str, payload: Dict[str, Any]) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **payload,
    }
    logger.info(json.dumps(payload, ensure_ascii=False))