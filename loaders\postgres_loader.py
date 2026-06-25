import pandas as pd
from typing import Literal


class PostgresLoader:
    """
    Loader for PostgreSQL using SQLAlchemy.
    Supports append, replace, and upsert modes.
    """

    def __init__(self, connection_string: str):
        try:
            from sqlalchemy import create_engine, text
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            self.text = text
        except ImportError:
            raise ImportError("Install: pip install sqlalchemy psycopg2-binary")

    def load(self, df: pd.DataFrame, table: str,
             if_exists: Literal["append", "replace", "fail"] = "append",
             schema: str = "public", chunksize: int = 1000) -> dict:
        """Load a DataFrame into a PostgreSQL table."""
        rows_before = len(df)
        df.to_sql(
            table, self.engine,
            schema=schema,
            if_exists=if_exists,
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        return {
            "table": f"{schema}.{table}",
            "rows_loaded": rows_before,
            "mode": if_exists,
        }

    def upsert(self, df: pd.DataFrame, table: str,
               conflict_cols: list[str], schema: str = "public") -> dict:
        """Upsert using PostgreSQL ON CONFLICT DO UPDATE."""
        from sqlalchemy.dialects.postgresql import insert
        from sqlalchemy import Table, MetaData

        meta = MetaData()
        meta.reflect(bind=self.engine, schema=schema, only=[table])
        tbl = meta.tables[f"{schema}.{table}"]

        records = df.to_dict("records")
        with self.engine.begin() as conn:
            stmt = insert(tbl).values(records)
            update_cols = {c: stmt.excluded[c] for c in df.columns if c not in conflict_cols}
            stmt = stmt.on_conflict_do_update(index_elements=conflict_cols, set_=update_cols)
            conn.execute(stmt)

        return {"table": table, "upserted_rows": len(df)}
