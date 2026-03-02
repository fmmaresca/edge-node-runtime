from fastapi import FastAPI
from .supervisor import Supervisor

def create_app(sup: Supervisor) -> FastAPI:
    app = FastAPI()

    @app.get("/v1/workloads")
    def workloads():
        out = []
        for name, st in sup._states.items():
            out.append({
                "name": name,
                "running": st.is_running(),
                "healthy": st.healthy,
                "pid": st.proc.pid if st.proc else None,

                "restarts_total": st.restarts_total,
                "last_start_ts": st.last_start_ts,
                "last_exit_code": st.last_exit_code,

                "last_health_status": st.last_health_status,
                "last_health_ok_ts": st.last_health_ok_ts,
            })
        return out

    return app

