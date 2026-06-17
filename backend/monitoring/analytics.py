import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"


class LogAnalyzer:
    def __init__(self, log_dir: Path = LOG_DIR):
        self.log_dir = log_dir

    def _read_logs(self, filename: str) -> list[dict]:
        filepath = self.log_dir / filename
        if not filepath.exists():
            return []
        entries = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries

    def analyze_chat_logs(self) -> dict[str, Any]:
        entries = self._read_logs("chat.log")
        if not entries:
            return {"status": "no_data"}

        total = len(entries)
        latencies = [e.get("response_time_ms", 0) for e in entries if e.get("response_time_ms")]
        tokens = [e.get("tokens", 0) for e in entries if e.get("tokens")]
        errors = [e for e in entries if e.get("status") == "error"]
        successes = [e for e in entries if e.get("status") == "success"]

        hourly_dist = Counter()
        daily_dist = Counter()
        for e in entries:
            ts = e.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    hourly_dist[dt.hour] += 1
                    daily_dist[dt.strftime("%Y-%m-%d")] += 1
                except ValueError:
                    continue

        top_users = Counter(e.get("user_id", "anonymous") for e in entries)

        return {
            "total_interactions": total,
            "success_count": len(successes),
            "error_count": len(errors),
            "error_rate": round(len(errors) / total, 4) if total else 0,
            "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0,
            "median_latency_ms": round(statistics.median(latencies), 2) if latencies else 0,
            "max_latency_ms": round(max(latencies), 2) if latencies else 0,
            "p95_latency_ms": round(
                sorted(latencies)[int(len(latencies) * 0.95)], 2
            ) if len(latencies) > 1 else 0,
            "avg_tokens": round(statistics.mean(tokens), 2) if tokens else 0,
            "total_tokens": sum(tokens),
            "hourly_distribution": dict(sorted(hourly_dist.items())),
            "daily_distribution": dict(sorted(daily_dist.items())),
            "top_users": top_users.most_common(10),
        }

    def analyze_error_logs(self) -> dict[str, Any]:
        entries = self._read_logs("error.log")
        if not entries:
            return {"status": "no_data"}

        error_types = Counter(e.get("error_type", "unknown") for e in entries)
        endpoints = Counter(e.get("endpoint", "unknown") for e in entries)
        return {
            "total_errors": len(entries),
            "error_types": dict(error_types.most_common()),
            "error_by_endpoint": dict(endpoints.most_common()),
        }

    def analyze_access_logs(self) -> dict[str, Any]:
        entries = self._read_logs("access.log")
        if not entries:
            return {"status": "no_data"}

        endpoints = Counter(e.get("endpoint", "unknown") for e in entries)
        methods = Counter(e.get("method", "UNKNOWN") for e in entries)
        users = Counter(e.get("user_id", "anonymous") for e in entries)
        statuses = Counter(str(e.get("http_status", 0)) for e in entries)

        latencies = [e.get("duration_ms", 0) for e in entries if e.get("duration_ms")]

        return {
            "total_requests": len(entries),
            "endpoints": dict(endpoints.most_common()),
            "methods": dict(methods.most_common()),
            "top_users": users.most_common(10),
            "status_distribution": dict(statuses.most_common()),
            "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0,
        }

    def detect_bottlenecks(self, threshold_ms: float = 5000) -> list[dict]:
        entries = self._read_logs("chat.log")
        slow_queries = []
        for e in entries:
            lat = e.get("response_time_ms", 0)
            if lat > threshold_ms:
                slow_queries.append(
                    {
                        "timestamp": e.get("timestamp"),
                        "user_id": e.get("user_id"),
                        "latency_ms": lat,
                        "tokens": e.get("tokens", 0),
                        "prompt_preview": (e.get("prompt") or "")[:100],
                    }
                )
        return sorted(slow_queries, key=lambda x: x["latency_ms"], reverse=True)[:20]

    def detect_anomalies(self, std_multiplier: float = 3.0) -> dict[str, Any]:
        entries = self._read_logs("chat.log")
        anomalies: dict[str, Any] = {"high_latency": [], "error_spikes": [], "usage_anomalies": []}

        if not entries:
            return anomalies

        latencies = [e.get("response_time_ms", 0) for e in entries if e.get("response_time_ms")]
        if len(latencies) > 1:
            mean = statistics.mean(latencies)
            stdev = statistics.stdev(latencies) if len(latencies) > 1 else 0
            threshold = mean + stdev * std_multiplier
            for e in entries:
                lat = e.get("response_time_ms", 0)
                if lat > threshold and lat > 1000:
                    anomalies["high_latency"].append(
                        {
                            "timestamp": e.get("timestamp"),
                            "latency_ms": lat,
                            "prompt_preview": (e.get("prompt") or "")[:80],
                        }
                    )

        hourly = Counter()
        for e in entries:
            ts = e.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    hourly[dt.strftime("%Y-%m-%d %H:00")] += 1
                except ValueError:
                    continue
        if hourly:
            counts = list(hourly.values())
            mean_c = statistics.mean(counts)
            std_c = statistics.stdev(counts) if len(counts) > 1 else 0
            threshold_c = mean_c + std_c * std_multiplier
            for period, count in hourly.items():
                if count > threshold_c:
                    anomalies["usage_anomalies"].append(
                        {"period": period, "request_count": count, "expected_max": round(threshold_c, 1)}
                    )

        return anomalies

    def full_report(self) -> dict[str, Any]:
        return {
            "chat": self.analyze_chat_logs(),
            "errors": self.analyze_error_logs(),
            "access": self.analyze_access_logs(),
            "bottlenecks": self.detect_bottlenecks(),
            "anomalies": self.detect_anomalies(),
            "generated_at": datetime.now().isoformat(),
        }
