from __future__ import annotations

import asyncio
import logging
import os
import signal
import time
from dataclasses import dataclass
from typing import Optional
import httpx

from .config import RuntimeCfg, WorkloadCfg
from . import metrics

log = logging.getLogger("edge_runtime.supervisor")



@dataclass
class WorkloadState:
    cfg: WorkloadCfg
    proc: Optional[asyncio.subprocess.Process] = None
    backoff_s: float = 0.0
    stopping: bool = False
    healthy: bool = False

    # persisted status fields (for API)
    restarts_total: int = 0
    last_start_ts: Optional[float] = None
    last_exit_code: Optional[int] = None
    last_health_ok_ts: Optional[float] = None
    last_health_status: Optional[int] = None

    def is_running(self) -> bool:
        return self.proc is not None and self.proc.returncode is None

class Supervisor:
    def __init__(self, cfg: RuntimeCfg):
        self.cfg = cfg
        self._stop_event = asyncio.Event()
        self._tasks: list[asyncio.Task] = []
        self._states: dict[str, WorkloadState] = {w.name: WorkloadState(cfg=w) for w in cfg.workloads}

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self.request_stop)
            except NotImplementedError:
                pass

        log.info("starting supervisor node_id=%s workloads=%d", self.cfg.node_id, len(self._states))

        # Start per-workload monitor loops
        for state in self._states.values():
            self._tasks.append(asyncio.create_task(self._monitor_workload(state), name=f"monitor:{state.cfg.name}"))

        # Uptime ticker
        self._tasks.append(asyncio.create_task(self._tick_metrics(), name="metrics-tick"))

        await self._stop_event.wait()
        log.info("stop requested, shutting down workloads...")
        await self._shutdown_all()

    def request_stop(self) -> None:
        self._stop_event.set()

    async def _tick_metrics(self) -> None:
        while not self._stop_event.is_set():
            metrics.tick_uptime()
            await asyncio.sleep(1.0)

    async def _monitor_workload(self, state: WorkloadState) -> None:
        name = state.cfg.name
        metrics.workload_last_exit_code.labels(workload=name).set(-1)
        metrics.workload_up.labels(workload=name).set(0)
        metrics.workload_healthy.labels(workload=name).set(0)
        state.healthy = False

        state.restarts_total = 0
        state.last_start_ts = None
        state.last_exit_code = None
        state.last_health_ok_ts = None
        state.last_health_status = None

        # initial backoff = configured base
        state.backoff_s = max(0.1, float(state.cfg.restart_backoff_s))

        while not self._stop_event.is_set():
            if not state.is_running() and not state.stopping:
                await self._start_workload(state)

            # Wait a bit, then check if it exited
            await asyncio.sleep(0.5)

            if state.proc is None:
                continue

            rc = state.proc.returncode
            if rc is None:
                continue  # still running

            # Exited

            state.last_exit_code = int(rc)  ## persistir
            metrics.workload_up.labels(workload=name).set(0)
            metrics.workload_healthy.labels(workload=name).set(0)
            state.healthy = False

            metrics.workload_last_exit_code.labels(workload=name).set(int(rc))
            log.warning("workload exited name=%s rc=%s", name, rc)

            state.proc = None

            if self._stop_event.is_set() or not state.cfg.restart:
                break

            # Backoff before restart
            metrics.workload_restarts_total.labels(workload=name).inc()
            state.restarts_total +=1
            log.info("restarting workload name=%s backoff_s=%.1f", name, state.backoff_s)
            await asyncio.sleep(state.backoff_s)
            state.backoff_s = min(state.backoff_s * 2.0, float(state.cfg.restart_backoff_max_s))

    async def _start_workload(self, state: WorkloadState) -> None:
        cfg = state.cfg
        name = cfg.name
        ts = time.time()

        env = os.environ.copy()
        env.update({str(k): str(v) for k, v in (cfg.env or {}).items()})

        log.info("starting workload name=%s cmd=%s", name, cfg.command)

        proc = await asyncio.create_subprocess_exec(
            *cfg.command,
            cwd=cfg.cwd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        state.proc = proc
        metrics.workload_up.labels(workload=name).set(1)
        state.last_start_ts = ts
        state.last_exit_code = None
        metrics.workload_last_start_timestamp.labels(workload=name).set(ts)
        if not (state.cfg.health and state.cfg.health.http):
            state.healthy = True
            metrics.workload_healthy.labels(workload=name).set(1)
        else:
            asyncio.create_task(self._healthcheck_loop(state))

        # stream logs
        asyncio.create_task(self._stream_workload_output(name, proc), name=f"logs:{name}")
        #
        if state.cfg.health and state.cfg.health.http:
            asyncio.create_task(self._healthcheck_loop(state))

    async def _healthcheck_loop(self, state: WorkloadState):
        cfg = state.cfg.health.http
        name = state.cfg.name

        async with httpx.AsyncClient() as client:
            while state.is_running() and not self._stop_event.is_set():
                status = None
                ok = False
                try:
                    r = await client.get(cfg.url, timeout=cfg.timeout_s)
                    status = int(r.status_code)
                    ok = (status == 200)
                except Exception:
                    status = None
                    ok = False

                state.last_health_status = status
                state.healthy = ok
                metrics.workload_healthy.labels(workload=name).set(1 if ok else 0)
                if ok:
                    state.last_health_ok_ts = time.time()

                await asyncio.sleep(cfg.interval_s)

    async def _shutdown_all(self) -> None:
        # Stop monitor loops from restarting
        for state in self._states.values():
            state.stopping = True

        # Terminate running procs
        for name, state in self._states.items():
            if state.proc is None or state.proc.returncode is not None:
                continue
            log.info("terminating workload name=%s", name)
            try:
                state.proc.terminate()
            except ProcessLookupError:
                pass

        # Wait, then kill if needed
        await asyncio.sleep(2.0)
        for name, state in self._states.items():
            if state.proc is None or state.proc.returncode is not None:
                continue
            log.warning("killing workload name=%s", name)
            try:
                state.proc.kill()
            except ProcessLookupError:
                pass

        # Cancel tasks
        for t in self._tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
