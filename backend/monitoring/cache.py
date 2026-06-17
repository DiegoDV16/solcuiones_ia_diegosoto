import hashlib
import json
import time
from threading import Lock
from typing import Any, Optional


class ResponseCache:
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        self._cache: dict[str, tuple[float, Any]] = {}
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._lock = Lock()
        self.hits = 0
        self.misses = 0

    def _make_key(self, prompt: str, session_id: str = "default") -> str:
        normalized = prompt.lower().strip()
        content_hash = hashlib.md5(normalized.encode()).hexdigest()
        sid_hash = hashlib.md5(session_id.encode()).hexdigest()
        return f"{sid_hash}:{content_hash}"

    def get(self, prompt: str, session_id: str = "default") -> Optional[Any]:
        key = self._make_key(prompt, session_id)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self.misses += 1
                return None
            timestamp, value = entry
            if time.time() - timestamp > self._ttl:
                del self._cache[key]
                self.misses += 1
                return None
            self.hits += 1
            return value

    def set(self, prompt: str, value: Any, session_id: str = "default"):
        key = self._make_key(prompt, session_id)
        with self._lock:
            if len(self._cache) >= self._max_size:
                oldest = min(self._cache.keys(), key=lambda k: self._cache[k][0])
                del self._cache[oldest]
            self._cache[key] = (time.time(), value)

    def invalidate(self, session_id: str):
        with self._lock:
            sid_hash = hashlib.md5(session_id.encode()).hexdigest()
            keys_to_delete = [k for k in self._cache if k.startswith(sid_hash)]
            for k in keys_to_delete:
                del self._cache[k]

    def clear(self):
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    @property
    def size(self) -> int:
        return len(self._cache)


response_cache = ResponseCache(ttl_seconds=300, max_size=500)
