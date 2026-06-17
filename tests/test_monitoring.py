import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.monitoring.logger import JSONFormatter, _setup_logger
from backend.monitoring.metrics import MetricsCollector
from backend.monitoring.security import Sanitizer, RateLimiter, Anonymizer
from backend.monitoring.cache import ResponseCache
from backend.monitoring.analytics import LogAnalyzer
from backend.monitoring.tracing import Tracer, Span


class TestLogging:
    def test_json_formatter(self):
        formatter = JSONFormatter()
        import logging
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        record.props = {"user_id": "test123"}
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "test message"
        assert parsed["user_id"] == "test123"
        assert "timestamp" in parsed

    def test_logger_creation(self):
        logger = _setup_logger("test_logger", "test.log")
        assert logger is not None
        assert logger.level == 10  # DEBUG


class TestMetrics:
    def setup_method(self):
        self.metrics = MetricsCollector()
        self.metrics.latencies = []
        self.metrics.ai_latencies = []
        self.metrics.total_requests = 0
        self.metrics.total_errors = 0
        self.metrics.total_tokens = 0

    def test_record_request(self):
        self.metrics.record_request("/api/chat", 150.0, "user1")
        assert self.metrics.total_requests == 1
        assert self.metrics.avg_latency_ms == 150.0

    def test_record_ai_interaction(self):
        self.metrics.record_ai_interaction(200.0, 50, success=True)
        self.metrics.record_ai_interaction(300.0, 75, success=False)
        assert self.metrics.total_tokens == 125
        assert self.metrics.total_errors == 1

    def test_error_rate(self):
        self.metrics.record_request("/api/test", 100.0)
        self.metrics.record_error("ValueError")
        assert self.metrics.total_errors == 1
        assert self.metrics.total_requests == 1
        assert self.metrics.error_rate == 1.0

    def test_snapshot(self):
        self.metrics.record_request("/api/chat", 100.0)
        self.metrics.record_ai_interaction(200.0, 50, success=True)
        snap = self.metrics.get_snapshot()
        assert "total_requests" in snap
        assert "avg_latency_ms" in snap
        assert "total_tokens" in snap


class TestSecurity:
    def test_sql_injection_detection(self):
        clean = Sanitizer.sanitize_input("SELECT * FROM users; DROP TABLE products;")
        assert "[FILTERED]" in clean

    def test_xss_detection(self):
        clean = Sanitizer.sanitize_input("<script>alert('xss')</script>")
        assert "[FILTERED]" in clean

    def test_clean_input_preserved(self):
        clean = Sanitizer.sanitize_input("Hola, ¿cuál es el precio del RTX 3060?")
        assert clean == "Hola, ¿cuál es el precio del RTX 3060?"

    def test_detect_injection(self):
        result = Sanitizer.detect_injection("DROP TABLE products")
        assert result is not None
        result = Sanitizer.detect_injection("Hola mundo")
        assert result is None

    def test_rate_limiter(self):
        rl = RateLimiter(max_requests=3, window_seconds=60)
        assert rl.is_allowed("test")
        assert rl.is_allowed("test")
        assert rl.is_allowed("test")
        assert not rl.is_allowed("test")
        assert rl.remaining("test") == 0

    def test_rate_limiter_different_keys(self):
        rl = RateLimiter(max_requests=2, window_seconds=60)
        assert rl.is_allowed("user1")
        assert rl.is_allowed("user2")
        assert rl.is_allowed("user1")
        assert not rl.is_allowed("user1")
        assert rl.is_allowed("user2")

    def test_anonymizer_hash(self):
        h1 = Anonymizer.hash_id("user123")
        h2 = Anonymizer.hash_id("user123")
        h3 = Anonymizer.hash_id("other")
        assert h1 == h2
        assert h1 != h3
        assert len(h1) == 16

    def test_anonymizer_ip(self):
        ip = Anonymizer.anonymize_ip("192.168.1.100")
        assert ip == "192.168.1.0"

    def test_anonymizer_text(self):
        text = Anonymizer.sanitize_text("<b>Hola</b> mundo", max_length=100)
        assert "<b>" not in text
        assert "Hola" in text


class TestCache:
    def setup_method(self):
        self.cache = ResponseCache(ttl_seconds=60, max_size=100)

    def test_cache_set_get(self):
        self.cache.set("test prompt", "test response")
        result = self.cache.get("test prompt")
        assert result == "test response"

    def test_cache_miss(self):
        result = self.cache.get("nonexistent")
        assert result is None

    def test_cache_hit_ratio(self):
        self.cache.set("key1", "val1")
        self.cache.get("key1")
        self.cache.get("key2")
        assert self.cache.hit_ratio == 0.5

    def test_cache_invalidate(self):
        self.cache.set("prompt1", "resp1", "session1")
        self.cache.invalidate("session1")
        result = self.cache.get("prompt1", "session1")
        assert result is None

    def test_cache_clear(self):
        self.cache.set("a", "b")
        self.cache.clear()
        assert self.cache.size == 0
        assert self.cache.hit_ratio == 0.0


class TestTracing:
    def setup_method(self):
        self.tracer = Tracer()

    def test_trace_creation(self):
        trace_id = self.tracer.start_trace()
        assert trace_id is not None

    def test_span_lifecycle(self):
        trace_id = self.tracer.start_trace()
        span = self.tracer.start_span("test_span", trace_id)
        with span:
            time.sleep(0.01)
        assert span.duration_ms > 0
        assert span.status == "ok"

    def test_span_error(self):
        trace_id = self.tracer.start_trace()
        span = self.tracer.start_span("error_span", trace_id)
        try:
            with span:
                raise ValueError("test error")
        except ValueError:
            pass
        assert span.status == "error"

    def test_trace_completed(self):
        trace_id = self.tracer.start_trace()
        s1 = self.tracer.start_span("span1", trace_id)
        with s1:
            pass
        result = self.tracer.trace_completed(trace_id)
        assert result["span_count"] == 1
        assert result["trace_id"] == trace_id


class TestAnalytics:
    def test_empty_logs(self):
        analyzer = LogAnalyzer(Path("/nonexistent"))
        result = analyzer.analyze_chat_logs()
        assert result["status"] == "no_data"

    def test_detect_bottlenecks_empty(self):
        analyzer = LogAnalyzer(Path("/nonexistent"))
        result = analyzer.detect_bottlenecks()
        assert result == []

    def test_detect_anomalies_empty(self):
        analyzer = LogAnalyzer(Path("/nonexistent"))
        result = analyzer.detect_anomalies()
        assert result["high_latency"] == []
