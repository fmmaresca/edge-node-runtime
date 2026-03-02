from __future__ import annotations

import time
from prometheus_client import Counter, Gauge

START_TIME = time.time()

runtime_uptime_seconds = Gauge(
    "edge_runtime_uptime_seconds",
    "Runtime process uptime in seconds.",
)

workload_up = Gauge(
    "edge_workload_up",
    "Whether the workload is currently running (1) or not (0).",
    labelnames=("workload",),
)

workload_restarts_total = Counter(
    "edge_workload_restarts_total",
    "Number of times a workload was restarted by the supervisor.",
    labelnames=("workload",),
)

workload_last_exit_code = Gauge(
    "edge_workload_last_exit_code",
    "Last exit code seen for the workload process (or -1 if unknown).",
    labelnames=("workload",),
)

workload_last_start_timestamp = Gauge(
    "edge_workload_last_start_timestamp",
    "Unix timestamp when workload was last started.",
    labelnames=("workload",),
)

workload_healthy = Gauge(
    "edge_workload_healthy",
    "Workload health status (1=healthy, 0=unhealthy)",
    labelnames=("workload",),
)

def tick_uptime() -> None:
    runtime_uptime_seconds.set(time.time() - START_TIME)
