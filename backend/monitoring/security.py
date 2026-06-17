import hashlib
import ipaddress
import re
import time
from collections import defaultdict
from threading import Lock
from typing import Optional


class Sanitizer:
    SQL_PATTERNS = [
        re.compile(r"(\bSELECT\b.*\bFROM\b)", re.I),
        re.compile(r"(\bDROP\b\s+\bTABLE\b)", re.I),
        re.compile(r"(\bDELETE\b\s+\bFROM\b)", re.I),
        re.compile(r"(\bINSERT\b\s+\bINTO\b)", re.I),
        re.compile(r"(\bUPDATE\b\s+\w+\s+SET\b)", re.I),
        re.compile(r"(\bALTER\b\s+\bTABLE\b)", re.I),
        re.compile(r"(\bUNION\b\s+.*\bSELECT\b)", re.I),
        re.compile(r"--", re.I),
        re.compile(r";", re.I),
        re.compile(r"\/\*", re.I),
    ]

    XSS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.I | re.S),
        re.compile(r"javascript\s*:", re.I),
        re.compile(r"on\w+\s*=", re.I),
        re.compile(r"<[^>]*>"),
    ]

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        if not text:
            return text
        sanitized = text
        for pattern in cls.SQL_PATTERNS:
            sanitized = pattern.sub("[FILTERED]", sanitized)
        for pattern in cls.XSS_PATTERNS:
            sanitized = pattern.sub("[FILTERED]", sanitized)
        return sanitized

    @classmethod
    def detect_injection(cls, text: str) -> Optional[str]:
        if not text:
            return None
        for pattern in cls.SQL_PATTERNS:
            if pattern.search(text):
                return f"SQL injection pattern detected: {pattern.pattern[:50]}"
        for pattern in cls.XSS_PATTERNS:
            if pattern.search(text):
                return f"XSS pattern detected: {pattern.pattern[:50]}"
        return None

    @classmethod
    def strip_html(cls, text: str) -> str:
        if not text:
            return text
        return re.sub(r"<[^>]*>", "", text)


class Anonymizer:
    @staticmethod
    def hash_id(value: Optional[str]) -> str:
        if not value:
            return "anonymous"
        return hashlib.sha256(value.encode()).hexdigest()[:16]

    @staticmethod
    def anonymize_ip(ip: Optional[str]) -> Optional[str]:
        if not ip:
            return None
        try:
            addr = ipaddress.ip_address(ip)
            if isinstance(addr, ipaddress.IPv4Address):
                return ".".join(ip.split(".")[:3] + ["0"])
            return "::".join(ip.split("::")[:1] + ["0:0:0:0"])
        except ValueError:
            return ip

    @staticmethod
    def sanitize_text(text: str, max_length: int = 2000) -> str:
        if not text:
            return text
        sanitized = Sanitizer.strip_html(text)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... [TRUNCATED]"
        return sanitized


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def _cleanup(self, key: str, now: float):
        window_start = now - self.window_seconds
        self._buckets[key] = [t for t in self._buckets[key] if t > window_start]

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            self._cleanup(key, now)
            count = len(self._buckets[key])
            if count >= self.max_requests:
                return False
            self._buckets[key].append(now)
            return True

    def remaining(self, key: str) -> int:
        now = time.time()
        with self._lock:
            self._cleanup(key, now)
            return max(0, self.max_requests - len(self._buckets[key]))

    def reset(self, key: str):
        with self._lock:
            self._buckets[key] = []


sanitizer = Sanitizer()
anonymizer = Anonymizer()
rate_limiter = RateLimiter(max_requests=60, window_seconds=60)
ai_rate_limiter = RateLimiter(max_requests=20, window_seconds=60)


def sanitize_chat_message(message: str) -> tuple[str, Optional[str]]:
    warning = Sanitizer.detect_injection(message)
    cleaned = Sanitizer.sanitize_input(message)
    return cleaned, warning
