"""
Business use cases - Electronic Billing
=======================================
Orchestrates electronic billing API use cases.
"""

import os
from datetime import date, datetime, timezone

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

    def _load_and_filter(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> pd.DataFrame:
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

        return filtered_df

    def _get_last_update(self) -> str:
        parquet_path = self.repository.parquet_file
        if parquet_path.exists():
            mtime = os.path.getmtime(str(parquet_path))
            return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        return datetime.now(tz=timezone.utc).isoformat()

    def get_summary(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> dict:
        df = self._load_and_filter(start_date, end_date, selected_users, selected_agreement)
        kpis = self.productivity_service.calculate_billing_summary(df)

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "last_update": self._get_last_update(),
            },
            "kpis": kpis,
        }

    def get_analytics(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
    ) -> dict:
        df = self._load_and_filter(start_date, end_date, selected_users, selected_agreement)
        analytics = self.productivity_service.calculate_billing_analytics(df)

        kpis = self.productivity_service.calculate_billing_summary(df)
        insights = self.productivity_service.generate_billing_insights(
            analytics,
            kpis["total_records"],
            kpis["total_valor_tercero"],
        )

        analytics["insights"] = insights
        return analytics

    def get_detail(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
        selected_agreement: str | None = None,
        page: int = 1,
        page_size: int = 50,
        filter_user: str | None = None,
        filter_eps: str | None = None,
        filter_convenio: str | None = None,
        filter_estado: str | None = None,
    ) -> dict:
        df = self._load_and_filter(start_date, end_date, selected_users, selected_agreement)

        user_col = next((c for c in ["USUARIO"] if c in df.columns), None)
        eps_col = next((c for c in ["EPS"] if c in df.columns), None)
        convenio_col = next((c for c in ["CONVENIO"] if c in df.columns), None)
        estado_col = next((c for c in ["ESTADO", "Estado"] if c in df.columns), None)

        if filter_user and user_col:
            df = df[df[user_col].astype(str).str.strip() == filter_user.strip()]
        if filter_eps and eps_col:
            df = df[df[eps_col].astype(str).str.strip() == filter_eps.strip()]
        if filter_convenio and convenio_col:
            df = df[df[convenio_col].astype(str).str.strip() == filter_convenio.strip()]
        if filter_estado and estado_col:
            df = df[df[estado_col].astype(str).str.strip() == filter_estado.strip()]

        total = len(df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_df = df.iloc[start_idx:end_idx]

        data = []
        for _, row in page_df.iterrows():
            item = {
                "identificacion": str(row.get("IDENTIFICACION", "")) if pd.notna(row.get("IDENTIFICACION")) else None,
                "prefijo": str(row.get("PREFIJO", "")) if "PREFIJO" in df.columns and pd.notna(row.get("PREFIJO")) else None,
                "factura": str(row.get("FACTURA", "")) if "FACTURA" in df.columns and pd.notna(row.get("FACTURA")) else None,
                "fecha_factura": str(row.get("FECHA FACTURA", ""))[:10] if "FECHA FACTURA" in df.columns and pd.notna(row.get("FECHA FACTURA")) else None,
                "fecha_legalizacion": str(row.get("FECHA LEGALIZACION", ""))[:10] if "FECHA LEGALIZACION" in df.columns and pd.notna(row.get("FECHA LEGALIZACION")) else None,
                "paciente": str(row.get("PACIENTE", "")) if "PACIENTE" in df.columns and pd.notna(row.get("PACIENTE")) else None,
                "valor_paciente": float(row.get("VALOR PACIENTE", 0)) if "VALOR PACIENTE" in df.columns and pd.notna(row.get("VALOR PACIENTE")) else None,
                "valor_tercero": float(row.get(VALUE_COLUMN, 0)) if pd.notna(row.get(VALUE_COLUMN)) else None,
                "eps": str(row.get(eps_col, "")) if eps_col and pd.notna(row.get(eps_col)) else None,
                "convenio": str(row.get(convenio_col, "")) if convenio_col and pd.notna(row.get(convenio_col)) else None,
                "usuario": str(row.get(user_col, "")) if user_col and pd.notna(row.get(user_col)) else None,
                "estado": str(row.get(estado_col, "")) if estado_col and pd.notna(row.get(estado_col)) else None,
            }
            data.append(item)

        filter_options = {
            "users": sorted(df[user_col].dropna().astype(str).unique().tolist()) if user_col and user_col in df.columns else [],
            "eps": sorted(df[eps_col].dropna().astype(str).unique().tolist()) if eps_col and eps_col in df.columns else [],
            "convenios": sorted(df[convenio_col].dropna().astype(str).unique().tolist()) if convenio_col and convenio_col in df.columns else [],
            "estado": sorted(df[estado_col].dropna().astype(str).unique().tolist()) if estado_col and estado_col in df.columns else [],
        }

        return {
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
            },
            "filters": filter_options,
            "data": data,
        }
