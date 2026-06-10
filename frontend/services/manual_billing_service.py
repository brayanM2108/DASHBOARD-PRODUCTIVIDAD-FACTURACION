"""Frontend service for manual billing (administrative processes)."""

from datetime import date
from typing import Optional

import pandas as pd

from frontend.api.manual_billing_api import ManualBillingApi
from frontend.models.manual_billing import ProcessRecord, ProcessSummary

REQUIRED_COLUMNS = ("FECHA", "NOMBRE", "PROCESO", "CANTIDAD")
ERROR_INPUT_NONE = "Input dataframe cannot be None."
ERROR_MISSING_COLUMNS = "Missing required columns: {columns}"


def _validate_required_columns(df: pd.DataFrame) -> None:
    if df is None:
        raise ValueError(ERROR_INPUT_NONE)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(ERROR_MISSING_COLUMNS.format(columns=", ".join(missing)))


class ManualBillingFrontendService:

    def __init__(self):
        self.api = ManualBillingApi()

    def get_records(
        self,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        proceso: Optional[str] = None,
    ) -> list[ProcessRecord]:
        raw = self.api.list_processes(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            proceso=proceso,
        )
        return [ProcessRecord(**r) for r in raw]

    def to_dataframe(self, records: list[ProcessRecord]) -> pd.DataFrame:
        if not records:
            return pd.DataFrame(columns=["FECHA", "NOMBRE", "DOCUMENTO", "PROCESO", "CANTIDAD", "OBSERVACION"])
        rows = [
            {
                "FECHA": pd.Timestamp(r.fecha),
                "NOMBRE": r.nombre,
                "DOCUMENTO": r.documento,
                "PROCESO": r.proceso,
                "CANTIDAD": r.cantidad,
                "OBSERVACION": r.observacion or "",
            }
            for r in records
        ]
        return pd.DataFrame(rows)

    def get_filter_options(self, records: list[ProcessRecord]) -> dict:
        df = self.to_dataframe(records)
        if df.empty:
            return {"people": [], "processes": []}
        people = sorted(df["NOMBRE"].dropna().astype(str).unique().tolist())
        processes = sorted(df["PROCESO"].dropna().astype(str).unique().tolist())
        return {"people": people, "processes": processes}

    def get_kpis(self, records: list[ProcessRecord]) -> dict:
        df = self.to_dataframe(records)
        try:
            _validate_required_columns(df)
        except ValueError:
            return {"total_records": 0, "total_quantity": 0, "unique_people": 0, "unique_processes": 0}
        if df.empty:
            return {"total_records": 0, "total_quantity": 0, "unique_people": 0, "unique_processes": 0}
        return {
            "total_records": len(df),
            "total_quantity": float(df["CANTIDAD"].fillna(0).sum()),
            "unique_people": int(df["NOMBRE"].nunique()),
            "unique_processes": int(df["PROCESO"].nunique()),
        }

    def get_summary(self, fecha_desde=None, fecha_hasta=None, proceso=None) -> ProcessSummary:
        raw = self.api.get_summary(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            proceso=proceso,
        )
        return ProcessSummary(**raw)

    def create_record(self, fecha: date, proceso: str, cantidad: int, observacion: Optional[str] = None) -> ProcessRecord:
        payload = {
            "fecha": fecha.isoformat(),
            "proceso": proceso,
            "cantidad": cantidad,
        }
        if observacion:
            payload["observacion"] = observacion
        raw = self.api.create_process(payload)
        return ProcessRecord(**raw)

    def delete_record(self, process_id: int) -> None:
        self.api.delete_process(process_id)

    def get_kpis_from_df(self, df: pd.DataFrame) -> dict:
        try:
            _validate_required_columns(df)
        except ValueError:
            return {"total_records": 0, "total_quantity": 0, "unique_people": 0, "unique_processes": 0}
        if df.empty:
            return {"total_records": 0, "total_quantity": 0.0, "unique_people": 0, "unique_processes": 0}
        normalized = df.copy()
        normalized["FECHA"] = pd.to_datetime(normalized["FECHA"], errors="coerce")
        normalized["CANTIDAD"] = pd.to_numeric(normalized["CANTIDAD"], errors="coerce")
        normalized = normalized.dropna(subset=["FECHA"])
        return {
            "total_records": len(normalized),
            "total_quantity": float(normalized["CANTIDAD"].fillna(0).sum()),
            "unique_people": int(normalized["NOMBRE"].nunique()),
            "unique_processes": int(normalized["PROCESO"].nunique()),
        }

    def build_chart_datasets(self, df: pd.DataFrame, selected_person=None, selected_process=None) -> dict:
        try:
            _validate_required_columns(df)
        except ValueError:
            empty = pd.DataFrame()
            return {"bar_by_person": empty, "pie_distribution": empty, "pie_mode": "process", "time_trend": empty}
        if df.empty:
            empty = pd.DataFrame()
            return {"bar_by_person": empty, "pie_distribution": empty, "pie_mode": "process", "time_trend": empty}
        normalized = df.copy()
        normalized["FECHA"] = pd.to_datetime(normalized["FECHA"], errors="coerce")
        normalized["CANTIDAD"] = pd.to_numeric(normalized["CANTIDAD"], errors="coerce")
        normalized = normalized.dropna(subset=["FECHA"])
        bar_by_person = normalized.groupby("NOMBRE")["CANTIDAD"].sum().reset_index()
        show_person_dist = (
            selected_process is not None
            and selected_process not in ("Todos", "All")
            and (selected_person is None or selected_person in ("Todos", "All"))
        )
        if show_person_dist:
            pie_distribution = normalized.groupby("NOMBRE")["CANTIDAD"].sum().reset_index()
            pie_mode = "person"
        else:
            pie_distribution = normalized.groupby("PROCESO")["CANTIDAD"].sum().reset_index()
            pie_mode = "process"
        time_trend = normalized.groupby("FECHA")["CANTIDAD"].sum().reset_index()
        return {
            "bar_by_person": bar_by_person,
            "pie_distribution": pie_distribution,
            "pie_mode": pie_mode,
            "time_trend": time_trend,
        }

    def filter_dataframe(self, df: pd.DataFrame, start_date=None, end_date=None, person=None, process=None) -> pd.DataFrame:
        try:
            _validate_required_columns(df)
        except ValueError:
            return df
        filtered = df.copy()
        filtered["FECHA"] = pd.to_datetime(filtered["FECHA"], errors="coerce")
        filtered["CANTIDAD"] = pd.to_numeric(filtered["CANTIDAD"], errors="coerce")
        filtered = filtered.dropna(subset=["FECHA"])
        if start_date:
            filtered = filtered[filtered["FECHA"] >= pd.Timestamp(start_date)]
        if end_date:
            filtered = filtered[filtered["FECHA"] <= pd.Timestamp(end_date)]
        if person:
            filtered = filtered[filtered["NOMBRE"] == person]
        if process:
            filtered = filtered[filtered["PROCESO"] == process]
        return filtered
