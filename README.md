# ETL Data Pipeline

A production-grade, modular ETL framework built in Python with a **FastAPI monitoring dashboard**. Supports multiple extraction sources (REST APIs, CSV files, PostgreSQL/MySQL databases), composable transformation steps, and loading to PostgreSQL or AWS S3.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  ETL Orchestrator                │
│                                                  │
│  [Extract] → [Transform] → [Load] → [Monitor]   │
└─────────────────────────────────────────────────┘
       │              │            │
  ┌────┴────┐   ┌─────┴─────┐  ┌──┴──────┐
  │ REST API│   │ DataCleaner│  │Postgres │
  │ CSV Dir │   │ Aggregator │  │ S3 /    │
  │ Database│   │ PivotTable │  │ Parquet │
  └─────────┘   └───────────┘  └─────────┘
```

## Features

- 🔌 **Multi-source extraction**: REST APIs (paginated), CSV directories, SQL databases
- 🔧 **Composable transformations**: null handling, deduplication, outlier removal, time rollups
- 💾 **Flexible loaders**: PostgreSQL (append/replace/upsert), AWS S3 (Parquet/CSV/JSON)
- 📊 **Live monitoring dashboard** at `/monitor/runs`
- 🔗 **Fluent pipeline API**: chain steps with `.add_step()`
- ⚡ **FastAPI REST trigger** for pipeline execution

## Quick Start

```bash
git clone https://github.com/AlaaDarwish282/etl-data-pipeline.git
cd etl-data-pipeline
pip install -r requirements.txt
python main.py
```

## Usage Example

```python
from pipeline.orchestrator import ETLPipeline
from extractors.csv_extractor import CSVExtractor
from transformers.data_cleaner import DataCleaner
from loaders.postgres_loader import PostgresLoader

extractor = CSVExtractor()
cleaner   = DataCleaner(null_strategy="fill_median")
loader    = PostgresLoader("postgresql://user:pass@localhost/db")

pipeline = (
    ETLPipeline("sales_pipeline")
    .add_step("extract", lambda _: extractor.extract("data/sales.csv"))
    .add_step("clean",   lambda df: cleaner.clean(df, numeric_cols=["revenue"]))
    .add_step("load",    lambda df: loader.load(df, "sales_clean") or df)
)

result = pipeline.run()
print(result)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/pipeline/run` | Trigger a pipeline run |
| GET | `/monitor/runs` | List recent pipeline runs |
| GET | `/monitor/runs/{name}` | Runs for a specific pipeline |
| GET | `/monitor/health` | Health check |

## License

MIT
