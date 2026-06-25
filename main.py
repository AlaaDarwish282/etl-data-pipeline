import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from monitoring.dashboard import router as monitor_router
from pipeline.orchestrator import ETLPipeline
from monitoring.dashboard import register_run

app = FastAPI(
    title="ETL Data Pipeline",
    description="Modular ETL framework with real-time monitoring",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(monitor_router)


class PipelineRunRequest(BaseModel):
    pipeline_name: str
    config: dict = {}


@app.get("/")
def root():
    return {"service": "ETL Data Pipeline", "docs": "/docs"}


@app.post("/api/v1/pipeline/run")
def run_pipeline(req: PipelineRunRequest):
    """Trigger a named pipeline run."""
    try:
        pipeline = ETLPipeline(req.pipeline_name)
        # Example: add a no-op step for demo; real pipelines inject steps via config
        pipeline.add_step("validate_config", lambda d: d or {})
        result = pipeline.run(initial_data=req.config)
        register_run(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
