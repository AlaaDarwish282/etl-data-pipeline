import pandas as pd
import io
from datetime import datetime


class S3Loader:
    """
    Loader for AWS S3. Supports CSV, Parquet, and JSON formats.
    """

    def __init__(self, bucket: str, aws_access_key: str = None,
                 aws_secret_key: str = None, region: str = "us-east-1"):
        try:
            import boto3
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region,
            )
        except ImportError:
            raise ImportError("Install: pip install boto3")
        self.bucket = bucket

    def _make_key(self, prefix: str, name: str, fmt: str) -> str:
        ts = datetime.utcnow().strftime("%Y/%m/%d")
        return f"{prefix}/{ts}/{name}.{fmt}"

    def load(self, df: pd.DataFrame, prefix: str, name: str,
             fmt: str = "parquet") -> dict:
        key = self._make_key(prefix, name, fmt)
        buf = io.BytesIO()

        if fmt == "parquet":
            df.to_parquet(buf, index=False)
        elif fmt == "csv":
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            buf = io.BytesIO(buf.getvalue().encode())
        elif fmt == "json":
            buf = io.BytesIO(df.to_json(orient="records").encode())
        else:
            raise ValueError(f"Unsupported format: {fmt}")

        buf.seek(0)
        self.s3.upload_fileobj(buf, self.bucket, key)
        return {"s3_path": f"s3://{self.bucket}/{key}", "rows": len(df), "format": fmt}
