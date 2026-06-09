"""Reusable productivity aggregations over DataFrames."""

import pandas as pd


def aggregate_records_by_user(
    df: pd.DataFrame,
    user_column: str = "USUARIO",
    date_column: str | None = None,
    group_by_date: bool = False,
    value_column: str | None = None,
) -> pd.DataFrame | None:
    """Aggregate records by user, optionally by date and/or value sum."""
    if df is None or df.empty or user_column not in df.columns:
        return None

    result_df = df.copy()

    if group_by_date and date_column and date_column in result_df.columns:
        result_df["DATE"] = pd.to_datetime(result_df[date_column], errors="coerce").dt.date
        if value_column and value_column in result_df.columns:
            return result_df.groupby([user_column, "DATE"], as_index=False).agg(
                COUNT=(user_column, "size"),
                VALOR_TERCERO=(value_column, "sum"),
            )
        return result_df.groupby([user_column, "DATE"]).size().reset_index(name="COUNT")

    if value_column and value_column in result_df.columns:
        return result_df.groupby(user_column, as_index=False).agg(
            COUNT=(user_column, "size"),
            VALOR_TERCERO=(value_column, "sum"),
        )

    return result_df.groupby(user_column).size().reset_index(name="COUNT")


def aggregate_records_by_date(df: pd.DataFrame, date_column: str) -> pd.DataFrame | None:
    """Aggregate row counts by date."""
    if df is None or df.empty or date_column not in df.columns:
        return None

    result_df = df.copy()
    result_df["DATE"] = pd.to_datetime(result_df[date_column], errors="coerce").dt.date
    result_df = result_df.dropna(subset=["DATE"])
    return result_df.groupby("DATE").size().reset_index(name="COUNT")


def aggregate_values_by_date(df: pd.DataFrame, date_column: str, value_column: str) -> pd.DataFrame | None:
    """Aggregate row counts and value sum by date."""
    if df is None or df.empty or date_column not in df.columns or value_column not in df.columns:
        return None

    result_df = df.copy()
    result_df["DATE"] = pd.to_datetime(result_df[date_column], errors="coerce").dt.date
    result_df = result_df.dropna(subset=["DATE"])
    return result_df.groupby("DATE", as_index=False).agg(
        REGISTROS=(date_column, "size"),
        VALOR_TERCERO=(value_column, "sum"),
    )


def top_by_count(by_user_df: pd.DataFrame | None, limit: int = 5) -> pd.DataFrame | None:
    """Return top rows by COUNT."""
    if by_user_df is None or by_user_df.empty or "COUNT" not in by_user_df.columns:
        return None
    return by_user_df.sort_values("COUNT", ascending=False).head(limit).reset_index(drop=True)

