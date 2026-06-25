import pandas as pd
from datetime import datetime
from typing import Callable, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class PipelineStep:
    def __init__(self, name: str, fn: Callable, enabled: bool = True):
        self.name = name
        self.fn = fn
        self.enabled = enabled


class ETLPipeline:
    """
    Orchestrator for multi-step ETL pipelines.
    Tracks execution time, row counts, and errors for each step.
    """

    def __init__(self, name: str):
        self.name = name
        self.steps: list[PipelineStep] = []
        self.run_log: list[dict] = []

    def add_step(self, name: str, fn: Callable, enabled: bool = True) -> "ETLPipeline":
        self.steps.append(PipelineStep(name, fn, enabled))
        return self  # fluent API

    def run(self, initial_data=None) -> dict:
        logger.info(f"Starting pipeline: {self.name}")
        started_at = datetime.utcnow()
        data = initial_data
        self.run_log = []

        for step in self.steps:
            if not step.enabled:
                logger.info(f"[SKIP] {step.name}")
                continue

            step_start = datetime.utcnow()
            try:
                data = step.fn(data)
                rows = len(data) if isinstance(data, pd.DataFrame) else None
                duration = (datetime.utcnow() - step_start).total_seconds()
                logger.info(f"[OK] {step.name} — {rows} rows — {duration:.2f}s")
                self.run_log.append({
                    "step": step.name, "status": "success",
                    "rows": rows, "duration_s": duration,
                })
            except Exception as e:
                duration = (datetime.utcnow() - step_start).total_seconds()
                logger.error(f"[FAIL] {step.name}: {e}")
                self.run_log.append({
                    "step": step.name, "status": "failed",
                    "error": str(e), "duration_s": duration,
                })
                raise

        total_duration = (datetime.utcnow() - started_at).total_seconds()
        logger.info(f"Pipeline {self.name} complete in {total_duration:.2f}s")
        return {
            "pipeline": self.name,
            "status": "success",
            "started_at": started_at.isoformat(),
            "duration_s": total_duration,
            "steps": self.run_log,
            "final_rows": len(data) if isinstance(data, pd.DataFrame) else None,
        }
