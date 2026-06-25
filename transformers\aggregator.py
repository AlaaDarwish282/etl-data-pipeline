import pandas as pd
from typing import Optional


class Aggregator:
    """
    Aggregation transformer for time-series and dimensional rollups.
    """

    def time_rollup(self, df: pd.DataFrame, date_col: str,
                    value_cols: list[str], freq: str = "M",
                    agg_funcs: list[str] = None) -> pd.DataFrame:
        """
        Aggregate time-series data by frequency.
        freq: 'D' (day), 'W' (week), 'M' (month), 'Q' (quarter), 'Y' (year)
        """
        agg_funcs = agg_funcs or ["sum", "mean", "count"]
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)

        agg_dict = {col: agg_funcs for col in value_cols}
        result = df[value_cols].resample(freq).agg(agg_dict)
        result.columns = ["_".join(c) for c in result.columns]
        result.reset_index(inplace=True)
        return result

    def group_rollup(self, df: pd.DataFrame, group_cols: list[str],
                     value_cols: list[str], agg_funcs: dict = None) -> pd.DataFrame:
        """Group-by aggregation with multiple metrics per column."""
        if agg_funcs is None:
            agg_funcs = {col: ["sum", "mean", "count", "std"] for col in value_cols}
        result = df.groupby(group_cols).agg(agg_funcs)
        result.columns = ["_".join(c) for c in result.columns]
        result.reset_index(inplace=True)
        return result

    def pivot_table(self, df: pd.DataFrame, index: str, columns: str,
                    values: str, aggfunc: str = "sum") -> pd.DataFrame:
        """Create a pivot table."""
        return df.pivot_table(index=index, columns=columns,
                              values=values, aggfunc=aggfunc, fill_value=0)
