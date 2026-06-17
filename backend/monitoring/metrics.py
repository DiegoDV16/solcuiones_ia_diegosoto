import time
import functools
from contextlib import contextmanager
from threading import Lock
from typing import Callable, Optional

try:
    import psutil

    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


class MetricsCollector:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def _initialize(self):
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            self.total_requests = 0
            self.total_errors = 0
            self.total_tokens = 0
            self.latencies: list[float] = []
            self.ai_latencies: list[float] = []
            self.requests_by_endpoint: dict[str, int] = {}
            self.requests_by_user: dict[str, int] = {}
            self.error_types: dict[str, int] = {}
            self.daily_queries: dict[str, int] = {}
            self.cache_hits = 0
            self.cache_misses = 0
            self.max_latency_samples = 10000
            self._initialized = True

    def __init__(self):
        self._initialize()

    def record_request(self, endpoint: str, duration_ms: float, user_id: Optional[str] = None):
        self.total_requests += 1
        self.latencies.append(duration_ms)
        if len(self.latencies) > self.max_latency_samples:
            self.latencies = self.latencies[-self.max_latency_samples:]
        self.requests_by_endpoint[endpoint] = self.requests_by_endpoint.get(endpoint, 0) + 1
        if user_id:
            self.requests_by_user[user_id] = self.requests_by_user.get(user_id, 0) + 1
        date_key = time.strftime("%Y-%m-%d")
        self.daily_queries[date_key] = self.daily_queries.get(date_key, 0) + 1

    def record_ai_interaction(self, duration_ms: float, tokens: int, success: bool):
        self.ai_latencies.append(duration_ms)
        if len(self.ai_latencies) > self.max_latency_samples:
            self.ai_latencies = self.ai_latencies[-self.max_latency_samples:]
        self.total_tokens += tokens
        if not success:
            self.total_errors += 1

    def record_error(self, error_type: str):
        self.total_errors += 1
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1

    def record_cache(self, hit: bool):
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    @property
    def avg_ai_latency_ms(self) -> float:
        if not self.ai_latencies:
            return 0.0
        return sum(self.ai_latencies) / len(self.ai_latencies)

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_errors / self.total_requests

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_lats = sorted(self.latencies)
        idx = int(len(sorted_lats) * 0.95)
        return sorted_lats[min(idx, len(sorted_lats) - 1)]

    @property
    def p99_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_lats = sorted(self.latencies)
        idx = int(len(sorted_lats) * 0.99)
        return sorted_lats[min(idx, len(sorted_lats) - 1)]

    @property
    def cache_hit_ratio(self) -> float:
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total

    @property
    def cpu_percent(self) -> float:
        if _HAS_PSUTIL:
            return psutil.cpu_percent(interval=None)
        return 0.0

    @property
    def memory_percent(self) -> float:
        if _HAS_PSUTIL:
            return psutil.virtual_memory().percent
        return 0.0

    @property
    def memory_used_mb(self) -> float:
        if _HAS_PSUTIL:
            return psutil.Process().memory_info().rss / (1024 * 1024)
        return 0.0

    def get_snapshot(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "total_tokens": self.total_tokens,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "avg_ai_latency_ms": round(self.avg_ai_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "p99_latency_ms": round(self.p99_latency_ms, 2),
            "error_rate": round(self.error_rate, 4),
            "cache_hit_ratio": round(self.cache_hit_ratio, 4),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": round(self.memory_used_mb, 2),
            "requests_by_endpoint": dict(self.requests_by_endpoint),
            "error_types": dict(self.error_types),
            "daily_queries": dict(self.daily_queries),
        }


metrics = MetricsCollector()


@contextmanager
def track_latency(endpoint: str, user_id: Optional[str] = None):
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = (time.perf_counter() - start) * 1000
        metrics.record_request(endpoint, duration, user_id)


def monitor_endpoint(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            metrics.record_error(type(e).__name__)
            raise
        finally:
            duration = (time.perf_counter() - start) * 1000
            metrics.record_request(func.__name__, duration)

    return wrapper
