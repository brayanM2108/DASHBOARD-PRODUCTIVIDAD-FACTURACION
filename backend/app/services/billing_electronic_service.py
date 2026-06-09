"""
Business use cases - Electronic Billing
=======================================
Orchestrates electronic billing API use cases.
"""

import pandas as pd

from ..core.exceptions.business import DataNotFoundException, ValidationException
from ..etl.billing_electronic_processor import (
    prepare_electronic_billing_df,
    VALUE_COLUMN,
)
from ..etl.filters.billing_filter import filter_electronic_billing
from ..repositories.parquet_repository import ParquetRepository
from .productivity_service import ProductivityService


class ElectronicBillingService:

    def __init__(
        self,
        repository: ParquetRepository,
        productivity_service: ProductivityService,
    ):
        self.repository = repository
        self.productivity_service = productivity_service

    def get_metrics(
        self,
        start_date,
        end_date,
        selected_users: list[str] | None = None,
        selected_agreement: str | list[str] | None = None,
    ) -> dict:
        df = self.repository.load()
        if df is None or df.empty:
            raise DataNotFoundException("No electronic billing data available")

        prepared_df = prepare_electronic_billing_df(df)
        if prepared_df is None or prepared_df.empty:
            raise ValidationException("Could not determine user column in electronic billing data")

        filtered_df = filter_electronic_billing(
            prepared_df,
            start_date,
            end_date,
            selected_users=selected_users,
            selected_agreement=selected_agreement,
        )

        if filtered_df is None or filtered_df.empty:
            raise DataNotFoundException("No matches found for the given filters")

        metrics = self.productivity_service.calculate_electronic_billing_productivity(filtered_df)

        return {
            "total_records": metrics.get("total_records", 0),
            "total_valor_tercero": metrics.get("total_valor_tercero", 0.0),
            "daily_avg_records": metrics.get("daily_avg_records", 0.0),
            "daily_avg_valor_tercero": metrics.get("daily_avg_valor_tercero", 0.0),
            "by_user": self._df_to_records(metrics.get("by_user_dual")),
            "by_date": self._df_to_records(metrics.get("by_date_dual")),
        }

    @staticmethod
    def _df_to_records(df: pd.DataFrame | None) -> list[dict]:
        if df is None or df.empty:
            return []
        result = df.copy()
        if "DATE" in result.columns:
            result["DATE"] = result["DATE"].astype(str)
        return result.to_dict(orient="records")
