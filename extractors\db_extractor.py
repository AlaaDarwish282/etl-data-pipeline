import pandas as pd
from typing import Optional
from datetime import datetime


class DBExtractor:
    """
    Database extractor using SQLAlchemy for multi-DB support
    (PostgreSQL, MySQL, SQLite, etc.)
    """

    def __init__(self, connection_string: str):
        """
        connection_string examples:
          postgresql://user:pass@host:5432/dbname
          mysql+pymysql://user:pass@host:3306/dbname
          sqlite:///local.db
        """
        try:
            from sqlalchemy import create_engine, text
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            self.text = text
        except ImportError:
            raise ImportError("Install sqlalchemy: pip install sqlalchemy")

    def extract(self, query: str, params: dict = None) -> pd.DataFrame:
        """Run a SELECT query and return results as DataFrame."""
        with self.engine.connect() as conn:
            df = pd.read_sql(self.text(query), conn, params=params or {})
        df["_extracted_at"] = datetime.utcnow().isoformat()
        return df

    def extract_table(self, table: str, schema: Optional[str] = None,
                      where: Optional[str] = None, limit: int = 100_000) -> pd.DataFrame:
        """Extract an entire table with optional filter and limit."""
        full_table = f"{schema}.{table}" if schema else table
        query = f"SELECT * FROM {full_table}"
        if where:
            query += f" WHERE {where}"
        query += f" LIMIT {limit}"
        return self.extract(query)

    def get_table_info(self, table: str) -> dict:
        """Get row count and column names for a table."""
        df_cols = self.extract(f"SELECT * FROM {table} LIMIT 1")
        count_df = self.extract(f"SELECT COUNT(*) AS cnt FROM {table}")
        return {
            "table": table,
            "columns": list(df_cols.columns),
            "row_count": int(count_df["cnt"].iloc[0]),
        }
