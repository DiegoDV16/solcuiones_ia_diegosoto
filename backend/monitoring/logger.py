import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "props"):
            log_entry.update(record.props)
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


def _setup_logger(name: str, log_file: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_DIR / log_file, encoding="utf-8")
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JSONFormatter())
    logger.addHandler(stream_handler)

    return logger


_chat_logger = _setup_logger("chat", "chat.log")
_api_logger = _setup_logger("api", "api.log")
_audit_logger = _setup_logger("audit", "audit.log")
_error_logger = _setup_logger("error", "error.log")
_access_logger = _setup_logger("access", "access.log")


def get_logger(name: str = "api") -> logging.Logger:
    return {
        "chat": _chat_logger,
        "api": _api_logger,
        "audit": _audit_logger,
        "error": _error_logger,
        "access": _access_logger,
    }.get(name, _api_logger)


def log_chat_interaction(
    user_id: str,
    prompt: str,
    response: str,
    response_time_ms: float,
    tokens: int,
    status: str,
    error: Optional[str] = None,
    endpoint: str = "/api/chat",
    http_status: int = 200,
    extra: Optional[dict] = None,
):
    entry: dict[str, Any] = {
        "user_id": Anonymizer.hash_id(user_id) if user_id else "anonymous",
        "prompt": Anonymizer.sanitize_text(prompt) if prompt else "",
        "response": Anonymizer.sanitize_text(response) if response else "",
        "response_time_ms": round(response_time_ms, 2),
        "tokens": tokens,
        "status": status,
        "error": error,
        "http_status": http_status,
        "endpoint": endpoint,
    }
    if extra:
        entry.update(extra)
    logger = get_logger("chat")
    logger.info("chat_interaction", extra={"props": entry})


def log_api_request(
    endpoint: str,
    method: str,
    user_id: Optional[str],
    http_status: int,
    duration_ms: float,
    ip: Optional[str] = None,
):
    entry: dict[str, Any] = {
        "endpoint": endpoint,
        "method": method,
        "user_id": Anonymizer.hash_id(user_id) if user_id else "anonymous",
        "http_status": http_status,
        "duration_ms": round(duration_ms, 2),
        "ip": Anonymizer.anonymize_ip(ip) if ip else None,
    }
    logger = get_logger("api")
    logger.info("api_request", extra={"props": entry})


def audit_log(
    action: str,
    user_id: Optional[str],
    resource: str,
    detail: Optional[str] = None,
    outcome: str = "success",
):
    entry: dict[str, Any] = {
        "action": action,
        "user_id": Anonymizer.hash_id(user_id) if user_id else "anonymous",
        "resource": resource,
        "detail": detail,
        "outcome": outcome,
    }
    logger = get_logger("audit")
    logger.info("audit_event", extra={"props": entry})


def log_error(
    error_type: str,
    message: str,
    endpoint: Optional[str] = None,
    user_id: Optional[str] = None,
    detail: Optional[str] = None,
):
    entry: dict[str, Any] = {
        "error_type": error_type,
        "message": message,
        "endpoint": endpoint,
        "user_id": Anonymizer.hash_id(user_id) if user_id else "anonymous",
        "detail": detail,
    }
    logger = get_logger("error")
    logger.error("error_event", extra={"props": entry})


from backend.monitoring.security import Anonymizer
