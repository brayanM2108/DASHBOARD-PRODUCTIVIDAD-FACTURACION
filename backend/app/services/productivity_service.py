"""Reusable productivity business service."""

import pandas as pd

from ..etl.aggregations.productivity import (
    aggregate_records_by_date,
    aggregate_records_by_user,
    aggregate_values_by_date,
)
from ..etl.validators import find_first_column_variant
from ..utils.config.settings import COLUMN_NAMES, COLUMN_NAMES_BILLING, COLUMN_NAMES_LEGALIZATIONS

VALUE_COLUMN = "VALOR TERCERO"


class ProductivityService:
    """Centralizes productivity metric use cases across modules."""

    @staticmethod
    def empty_record_metrics(category: str | None = None) -> dict:
        result = {
            "total": 0,
            "by_user": [],
            "by_date": [],
            "daily_average": 0,
        }
        if category is not None:
            result["category"] = category
        return result

    @staticmethod
    def calculate_record_productivity(
            df: pd.DataFrame,
            user_column_variants=None,
            date_column_variants=None,
            category: str | None = None,
    ) -> dict:
        """Calculate row-count productivity metrics by user and date."""

        if df is None or df.empty:
            return ProductivityService.empty_record_metrics(
                category=category
            )

        user_variants = (
                user_column_variants
                or COLUMN_NAMES["usuario"]
        )

        date_variants = (
                date_column_variants
                or COLUMN_NAMES["fecha"]
        )

        user_col = find_first_column_variant(
            df,
            user_variants,
        )

        date_col = find_first_column_variant(
            df,
            date_variants,
        )

        by_user_df = (
            aggregate_records_by_user(
                df,
                user_col,
                date_col,
                group_by_date=False,
            )
            if user_col
            else None
        )

        by_date_df = (
            aggregate_records_by_date(
                df,
                date_col,
            )
            if date_col
            else None
        )

        daily_average = 0.0

        if by_date_df is not None and not by_date_df.empty:

            daily_average = float(
                by_date_df["COUNT"].mean()
            )

        if by_user_df is not None:

            by_user_df = by_user_df.rename(
                columns={
                    "COUNT": "REGISTROS",
                }
            )

            by_user = by_user_df.to_dict(
                orient="records"
            )

        else:

            by_user = []

        if by_date_df is not None:

            by_date_df = by_date_df.rename(
                columns={
                    "COUNT": "REGISTROS",
                }
            )

            by_date_df["DATE"] = (
                by_date_df["DATE"]
                .astype(str)
            )

            by_date = by_date_df.to_dict(
                orient="records"
            )

        else:

            by_date = []

        result = {
            "total": len(df),
            "daily_average": daily_average,
            "by_user": by_user,
            "by_date": by_date,
        }

        if category is not None:
            result["category"] = category

        return result

    @staticmethod
    def calculate_legalizations_productivity(df: pd.DataFrame, category: str = "PPL") -> dict:
        """Calculate legalizations productivity preserving existing response shape."""
        return ProductivityService.calculate_record_productivity(
            df,
            user_column_variants=COLUMN_NAMES_LEGALIZATIONS["usuario"],
            date_column_variants=list(COLUMN_NAMES_LEGALIZATIONS["fecha"]) + ["FECHA REAL"],
            category=category,
        )

    @staticmethod
    def empty_billing_metrics() -> dict:
        return {
            "total": 0,
            "by_user": None,
            "by_date": None,
            "daily_average": 0,
            "total_records": 0,
            "total_valor_tercero": 0.0,
            "by_user_dual": None,
            "by_date_dual": None,
            "daily_avg_records": 0.0,
            "daily_avg_valor_tercero": 0.0,
        }

    @staticmethod
    def calculate_electronic_billing_productivity(df: pd.DataFrame) -> dict:
        """Calculate electronic billing productivity using shared aggregators."""
        if df is None or df.empty:
            return ProductivityService.empty_billing_metrics()

        user_col = find_first_column_variant(df, COLUMN_NAMES_BILLING.get("usuario", []))
        date_col = find_first_column_variant(df, COLUMN_NAMES_BILLING.get("fecha", []))
        if VALUE_COLUMN not in df.columns:
            return ProductivityService.empty_billing_metrics()

        total_records = int(len(df))
        total_valor = float(df[VALUE_COLUMN].sum())

        by_user_dual = None
        by_user_legacy = None
        if user_col:
            by_user_dual = aggregate_records_by_user(
                df, user_col, value_column=VALUE_COLUMN,
            )
            if by_user_dual is not None and not by_user_dual.empty:
                by_user_dual = by_user_dual.sort_values("VALOR_TERCERO", ascending=False)
                by_user_legacy = (
                    by_user_dual[[user_col, "VALOR_TERCERO"]]
                    .rename(columns={"VALOR_TERCERO": "COUNT"})
                    .sort_values("COUNT", ascending=False)
                )

        by_date_dual = None
        by_date_legacy = None
        if date_col:
            by_date_dual = aggregate_values_by_date(df, date_col, VALUE_COLUMN)
            if by_date_dual is not None and not by_date_dual.empty:
                by_date_dual = by_date_dual.sort_values("DATE")
                by_date_legacy = (
                    by_date_dual[["DATE", "VALOR_TERCERO"]]
                    .rename(columns={"VALOR_TERCERO": "COUNT"})
                    .sort_values("DATE")
                )

        daily_avg_records = 0.0
        daily_avg_valor = 0.0
        if by_date_dual is not None and not by_date_dual.empty:
            daily_avg_records = float(by_date_dual["REGISTROS"].mean())
            daily_avg_valor = float(by_date_dual["VALOR_TERCERO"].mean())

        return {
            "total": total_valor,
            "by_user": by_user_legacy,
            "by_date": by_date_legacy,
            "daily_average": daily_avg_valor,
            "total_records": total_records,
            "total_valor_tercero": total_valor,
            "by_user_dual": by_user_dual,
            "by_date_dual": by_date_dual,
            "daily_avg_records": daily_avg_records,
            "daily_avg_valor_tercero": daily_avg_valor,
        }
