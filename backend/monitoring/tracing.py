import time
import uuid
from contextvars import ContextVar
from typing import Any, Optional

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
trace_context: ContextVar[dict] = ContextVar("trace_context", default={})


class Span:
    def __init__(self, name: str, parent_id: Optional[str] = None):
        self.name = name
        self.span_id = uuid.uuid4().hex[:12]
        self.parent_id = parent_id
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.attributes: dict[str, Any] = {}
        self.status = "ok"

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        if exc_type:
            self.status = "error"
            self.attributes["error"] = str(exc_val)

    @property
    def duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def to_dict(self) -> dict:
        return {
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "attributes": self.attributes,
        }


class Tracer:
    def __init__(self):
        self.traces: dict[str, list[Span]] = {}

    def start_trace(self, trace_id: Optional[str] = None) -> str:
        tid = trace_id or uuid.uuid4().hex
        self.traces[tid] = []
        return tid

    def start_span(self, name: str, trace_id: str, parent_id: Optional[str] = None) -> Span:
        span = Span(name, parent_id)
        if trace_id not in self.traces:
            self.traces[trace_id] = []
        self.traces[trace_id].append(span)
        return span

    def get_trace(self, trace_id: str) -> list[dict]:
        spans = self.traces.get(trace_id, [])
        return [s.to_dict() for s in spans]

    def trace_completed(self, trace_id: str) -> dict:
        spans = self.get_trace(trace_id)
        if not spans:
            return {"trace_id": trace_id, "spans": [], "total_duration_ms": 0}
        total_ms = sum(s["duration_ms"] for s in spans)
        return {
            "trace_id": trace_id,
            "spans": spans,
            "total_duration_ms": round(total_ms, 2),
            "span_count": len(spans),
        }

    def export_to_json(self, trace_id: str) -> str:
        import json
        return json.dumps(self.trace_completed(trace_id), indent=2, ensure_ascii=False)


tracer = Tracer()
