import pandas as pd
import numpy as np
from typing import Optional


class DataCleaner:
    """
    Data cleaning transformer: handles nulls, duplicates,
    type coercion, and outlier detection.
    """

    def __init__(self, null_strategy: str = "drop", outlier_std: float = 3.0):
        self.null_strategy = null_strategy   # 'drop' | 'fill_mean' | 'fill_median' | 'fill_zero'
        self.outlier_std = outlier_std
        self.report: dict = {}

    def clean(self, df: pd.DataFrame, numeric_cols: list[str] = None) -> pd.DataFrame:
        original_rows = len(df)
        df = df.copy()

        # Drop duplicate rows
        df.drop_duplicates(inplace=True)
        dupes_removed = original_rows - len(df)

        # Handle nulls
        null_counts = df.isnull().sum().to_dict()
        if self.null_strategy == "drop":
            df.dropna(inplace=True)
        elif self.null_strategy == "fill_mean":
            for col in df.select_dtypes(include=np.number).columns:
                df[col].fillna(df[col].mean(), inplace=True)
        elif self.null_strategy == "fill_median":
            for col in df.select_dtypes(include=np.number).columns:
                df[col].fillna(df[col].median(), inplace=True)
        elif self.null_strategy == "fill_zero":
            df.fillna(0, inplace=True)

        # Remove outliers in specified numeric columns
        outliers_removed = 0
        if numeric_cols:
            for col in numeric_cols:
                if col in df.columns:
                    mean, std = df[col].mean(), df[col].std()
                    mask = (df[col] - mean).abs() <= self.outlier_std * std
                    outliers_removed += (~mask).sum()
                    df = df[mask]

        self.report = {
            "original_rows": original_rows,
            "final_rows": len(df),
            "duplicates_removed": dupes_removed,
            "outliers_removed": int(outliers_removed),
            "null_counts_before": null_counts,
        }
        return df

    def get_report(self) -> dict:
        return self.report
