# edge-node-runtime

Lightweight edge runtime for remote infrastructure with on-device anomaly detection.

---

## 🎯 Goal

Build a **portfolio-grade project** that demonstrates:

- Long-running production services
- Remote configuration management
- Self-healing / watchdog patterns
- Plugin-based task execution
- Observability (metrics-first design)
- On-device anomaly detection (real AI, no hype)

This project becomes the **core platform** that can later run other agents (e.g. netprobe).

---

## 🧠 Positioning

This is not an IoT demo.

It represents:

> Software platform for remote instrumentation nodes

Target perception:

- Edge / IoT platform engineer
- Infrastructure & distributed systems
- Linux production environments
- Remote / unreliable field deployments

---

## 🧱 High-Level Architecture

```
edge-node-runtime
├── runtime daemon
├── task / plugin runner
├── local config
├── remote config client
├── metrics exporter
└── anomaly detection module
```

Control & observability stack (demo environment):

```
docker-compose
├── edge node
├── MQTT (or NATS)
├── Prometheus
└── Grafana
```

---

## ⚙️ Tech Stack

Aligned with real production environments:

- Python
- asyncio
- FastAPI (control plane only)
- Prometheus client
- systemd service (real deployment model)

AI / anomaly detection:

- scikit-learn
- statsmodels

---

## 🚀 Roadmap

### v0.1 — Local Runtime (MVP)

Core functionality:

- Daemon process
- Task runner
- Structured logging
- Local configuration file
- Prometheus metrics endpoint

Goal:

A real long-running service that can be installed and managed via systemd.

---

### v0.2 — Remote Control Plane

- Remote config pull
- Config versioning
- Hot reload
- Plugin system

Goal:

Demonstrate fleet-manageable nodes.

---

### v0.3 — On-Device Anomaly Detection

Run anomaly detection on:

- Latency
- Resource usage
- Task timing
- Network quality metrics

Possible models:

- IsolationForest
- STL + residual analysis

Output:

- Local alert events
- Prometheus metrics

Key message:

> On-device ML for autonomous infrastructure monitoring

---

## 🔌 Plugin System (Future Integration Point)

Plugins will allow:

- netprobe agent
- RF telemetry collectors
- Custom field instrumentation

This turns the runtime into a **reusable edge platform**.

---

## 🧪 Demo Scenario

`docker-compose up` should bring:

- A running node
- Live metrics in Prometheus
- Grafana dashboard
- Example anomaly detection event

This is critical for recruiter UX.

---

## 📦 Deliverables for Portfolio

Repository must include:

- Architecture diagram
- Quickstart in 2–3 commands
- systemd unit example
- Screenshot of Grafana with anomaly
- Clean README focused on real-world use

---

## 🌐 Relationship with Other Projects

This project becomes the core of the ecosystem:

- rf-site-telemetry → data acquisition
- edge-node-runtime → node platform
- netprobe → network observability plugin

---

## 🧭 Success Criteria

This is **portfolio complete** when:

- It looks deployable on a real remote node
- It exposes real metrics
- It survives restarts
- It runs at least one plugin
- It produces one meaningful anomaly event

Not when it has more features.

---

## ⛔ Non-Goals

To keep the scope tight:

- No Kubernetes
- No cloud lock-in
- No complex UI
- No fake AI

---

## 🏁 Next Step

Create the repository and implement:

**v0.1 — Local Runtime MVP**

