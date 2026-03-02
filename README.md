# edge-node-runtime

A small “edge supervisor” runtime: run and monitor one or more local workloads, expose Prometheus metrics, and provide a minimal control API for fleet-style visibility.

This repo is a **portfolio-grade demo**: simple enough to read in one sitting, real enough to deploy on a Linux VM with systemd.

---

## What it does

- **Supervises workloads** (starts processes, restarts on failure with backoff)
- **Health checks** (HTTP polling per workload; separates *running* vs *healthy*)
- **Observability-first**
  - Prometheus metrics at `/metrics`
  - JSON status endpoint with restart counters & last-known health
- **Real deployment model** (systemd unit included)

---

## Live demo (public)

- Workload status (JSON):  
  https://rfdemo.fmaresca.com/edge/workloads

- Prometheus metrics:  
  https://rfdemo.fmaresca.com/edge/metrics

- Grafana dashboard:  
  https://rfdemo.fmaresca.com/grafana/

---

## Architecture (high level)

```
┌──────────────────────┐
│   edge-node-runtime  │
│                      │
│  supervisor loop     │
│  /metrics            │
│  /v1/workloads       │
└──────────┬───────────┘
           │
           │ spawns
           ▼
┌──────────────────────┐        ┌──────────────────────┐
│   local workloads    │        │  health endpoints    │
│  (uvicorn, agents,   │◄──────►│   HTTP polling       │
│   telemetry, etc.)   │        └──────────────────────┘
└──────────────────────┘
           │
           ▼
   Prometheus / Grafana
   (optional)
```

---

## Endpoints

By default (see `config/edge-runtime.example.yaml`):

- **Metrics:** `http://<node>:9108/metrics`
- **Control API (JSON):** `http://127.0.0.1:9180/v1/workloads`

### Example `/v1/workloads`

```json
[
  {
    "name": "rf-site-telemetry",
    "running": true,
    "healthy": true,
    "pid": 1234,
    "restarts_total": 0,
    "last_start_ts": 1772275618.09,
    "last_exit_code": null,
    "last_health_status": 200,
    "last_health_ok_ts": 1772275632.19
  }
]
```

---

## Quickstart (dev)

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .

edge-runtime --config config/edge-runtime.example.yaml

curl -s localhost:9108/metrics | head
curl -s 127.0.0.1:9180/v1/workloads | python -m json.tool
```

---

## Configuration

See: `config/edge-runtime.example.yaml`

Key concepts:

- `workloads[].command` → argv list to spawn
- `workloads[].restart` → enable restart loop
- `workloads[].health.http.url` → optional HTTP health endpoint
- `metrics.listen/port` → Prometheus endpoint
- `control_api.listen/port` → JSON status endpoint (recommended localhost-only)

---

## Running real workloads (example: uvicorn app)

```yaml
workloads:
  - name: rf-site-telemetry
    cwd: /opt/rfsite
    command:
      - /opt/rfsite/venv/bin/python3
      - /opt/rfsite/venv/bin/uvicorn
      - app.main:app
      - --host
      - 127.0.0.1
      - --port
      - "8001"
    restart: true
    restart_backoff_s: 2
    restart_backoff_max_s: 30
    health:
      http:
        url: "http://127.0.0.1:8001/healthz"
        interval_s: 5
        timeout_s: 2
```

---

## systemd install (Linux)

This repo includes a sample unit:

`packaging/systemd/edge-runtime.service`

```bash
sudo cp packaging/systemd/edge-runtime.service /etc/systemd/system/edge-runtime.service
sudo systemctl daemon-reload
sudo systemctl enable --now edge-runtime
sudo journalctl -u edge-runtime -n 100 --no-pager
```

---

## Why this exists

Most “IoT demos” are one-off scripts.

This project focuses on the boring, real stuff you need in field nodes:

- long-running process management
- recoverability (restarts, backoff)
- health vs up
- metrics-first design
- simple deployment story (systemd)

---

## Roadmap

See `docs/roadmap.md`.

---

## License

MIT
