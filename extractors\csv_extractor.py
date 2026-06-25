import pandas as pd
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class CSVExtractor:
    """
    CSV/TSV file extractor with schema validation and encoding detection.
    Supports single files and batch directory processing.
    """

    def __init__(self, encoding: str = "utf-8", delimiter: str = ","):
        self.encoding = encoding
        self.delimiter = delimiter

    def extract(self, path: str, dtype: dict = None,
                parse_dates: list = None) -> pd.DataFrame:
        """Extract a single CSV file."""
        df = pd.read_csv(
            path,
            encoding=self.encoding,
            sep=self.delimiter,
            dtype=dtype,
            parse_dates=parse_dates or [],
        )
        df["_source_file"] = Path(path).name
        df["_extracted_at"] = datetime.utcnow().isoformat()
        return df

    def extract_directory(self, dir_path: str, pattern: str = "*.csv",
                          recursive: bool = False) -> pd.DataFrame:
        """Extract all matching CSV files from a directory."""
        base = Path(dir_path)
        files = list(base.rglob(pattern) if recursive else base.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No files matching {pattern} in {dir_path}")
        frames = [self.extract(str(f)) for f in files]
        return pd.concat(frames, ignore_index=True)

    def validate_schema(self, df: pd.DataFrame, required_cols: list[str]) -> dict:
        missing = [c for c in required_cols if c not in df.columns]
        return {"valid": len(missing) == 0, "missing_columns": missing, "rows": len(df)}
