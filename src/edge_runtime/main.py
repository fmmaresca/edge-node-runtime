from __future__ import annotations

import argparse
import asyncio
import logging
import threading

import uvicorn
from prometheus_client import start_http_server

from .api import create_app
from .config import load_config
from .supervisor import Supervisor
from .util.logging import setup_logging

log = logging.getLogger("edge_runtime")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="edge-runtime")
    p.add_argument("--config", required=True, help="Path to YAML config.")
    p.add_argument("--log-level", default="INFO", help="DEBUG|INFO|WARNING|ERROR")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)

    cfg = load_config(args.config)
    log.info(
        "config loaded node_id=%s workloads=%d metrics=%s:%d",
        cfg.node_id, len(cfg.workloads), cfg.metrics.listen, cfg.metrics.port
    )

    sup = Supervisor(cfg)

    # 1) Metrics endpoint (Prometheus scrape)
    start_http_server(addr=cfg.metrics.listen, port=cfg.metrics.port)
    log.info("metrics listening on http://%s:%d/metrics", cfg.metrics.listen, cfg.metrics.port)

    # 2) Control API (JSON) in background thread
    app = create_app(sup)

    def run_api():
        try:
            log.info("control API starting on http://%s:%d", cfg.control_api.listen, cfg.control_api.port)
            uvicorn.run(
                app,
                host=cfg.control_api.listen,
                port=cfg.control_api.port,
                log_level="warning",
            )
        except Exception:
            log.exception("control API failed to start")

    threading.Thread(target=run_api, daemon=True).start()

    # 3) Supervisor main loop (blocking)
    asyncio.run(sup.run())
