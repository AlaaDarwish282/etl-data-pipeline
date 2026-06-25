from fastapi import APIRouter
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/monitor", tags=["monitoring"])

# In-memory run registry (replace with DB in production)
_runs: list[dict] = []


def register_run(run_result: dict) -> None:
    _runs.append({**run_result, "registered_at": datetime.utcnow().isoformat()})
    if len(_runs) > 500:
        _runs.pop(0)


@router.get("/runs")
def list_runs(limit: int = 20, status: Optional[str] = None):
    runs = _runs if not status else [r for r in _runs if r.get("status") == status]
    return {"total": len(runs), "runs": runs[-limit:][::-1]}


@router.get("/runs/{pipeline_name}")
def get_pipeline_runs(pipeline_name: str, limit: int = 10):
    runs = [r for r in _runs if r.get("pipeline") == pipeline_name]
    return {"pipeline": pipeline_name, "total": len(runs), "runs": runs[-limit:][::-1]}


@router.get("/health")
def health():
    return {"status": "ok", "total_runs": len(_runs)}
