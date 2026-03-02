from typing import List, Optional
from pydantic import BaseModel, Field
import yaml

class MetricsCfg(BaseModel):
    listen: str = "0.0.0.0"
    port: int = 9108

class ControlApiCfg(BaseModel):
    listen: str = "127.0.0.1"
    port: int = 9180

class HealthHttpCfg(BaseModel):
    url: str
    interval_s: float = 5.0
    timeout_s: float = 2.0

class HealthCfg(BaseModel):
    http: Optional[HealthHttpCfg] = None

class WorkloadCfg(BaseModel):
    name: str
    command: List[str]
    health: Optional[HealthCfg] = None
    cwd: Optional[str] = None
    env: dict[str, str] = Field(default_factory=dict)
    restart: bool = True
    restart_backoff_s: float = 2.0
    restart_backoff_max_s: float = 30.0

class RuntimeCfg(BaseModel):
    node_id: str = "edge-001"
    metrics: MetricsCfg = MetricsCfg()
    control_api: ControlApiCfg = ControlApiCfg()
    workloads: List[WorkloadCfg] = Field(default_factory=list)

def load_config(path: str) -> RuntimeCfg:
    with open(path) as f:
        return RuntimeCfg.model_validate(yaml.safe_load(f))
