import pandas as pd

from ..core.exceptions.business import DataNotFoundException
from ..etl.radicacion_processor import prepare_radicacion_df
from ..repositories.parquet_repository import ParquetRepository


class RadicacionService:

    def __init__(self, repository: ParquetRepository):
        self.repository = repository

    def get_metrics(
        self,
        start_date=None,
        end_date=None,
        selected_users: list[str] | None = None,
    ) -> dict:
        df = self.repository.load()
        if df is None or df.empty:
            raise DataNotFoundException("No hay datos de facturación electrónica")

        prepared_df = prepare_radicacion_df(df)
        if prepared_df is None or prepared_df.empty:
            raise DataNotFoundException("No se pudieron preparar los datos de radicación")

        fecha_col = "FECHA FACTURA"
        if fecha_col in prepared_df.columns:
            if start_date:
                prepared_df = prepared_df[prepared_df[fecha_col].dt.date >= start_date]
            if end_date:
                prepared_df = prepared_df[prepared_df[fecha_col].dt.date <= end_date]

        user_col = "USUARIO"
        if selected_users and user_col in prepared_df.columns:
            selected_set = {str(u).strip().upper() for u in selected_users}
            prepared_df = prepared_df[
                prepared_df[user_col].astype(str).str.strip().str.upper().isin(selected_set)
            ]

        total = len(prepared_df)
        vencidas = int(prepared_df["VENCIDA"].sum()) if "VENCIDA" in prepared_df.columns else 0
        pct_vencidas = round((vencidas / total * 100), 1) if total > 0 else 0.0

        by_user = []
        if user_col in prepared_df.columns:
            user_agg = (
                prepared_df.groupby(user_col)
                .agg(TOTAL=("VENCIDA", "count"), VENCIDAS=("VENCIDA", "sum"))
                .reset_index()
            )
            user_agg["VENCIDAS"] = user_agg["VENCIDAS"].astype(int)
            user_agg = user_agg.sort_values("VENCIDAS", ascending=False)
            by_user = user_agg.to_dict(orient="records")

        return {
            "total": total,
            "vencidas": vencidas,
            "porcentaje_vencidas": pct_vencidas,
            "by_user": by_user,
        }
