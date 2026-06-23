from datetime import date

import pandas as pd

from ..core.exceptions.business import ValidationException
from ..etl.billers_processor import filter_by_billers_document
from ..etl.filters.rips_filter import filter_rips
from ..etl.transformers.rips_transformer import prepare_rips_dataframe
from ..etl.validators.rips_validator import validate_rips_dataframe
from ..repositories.parquet_repository import ParquetRepository
from ..utils.config.settings import COLUMN_NAMES_RIPS, SECONDS_PER_RECORD_RIPS
from .productivity_service import ProductivityService


def process_rips(df: pd.DataFrame, df_facturadores=None) -> dict:
    if df is None or df.empty:
        return {"error": "El archivo RIPS no contiene registros.", "rips_df": None}

    is_valid, message = validate_rips_dataframe(df)
    if not is_valid:
        return {"error": message, "rips_df": None}

    rips_df = prepare_rips_dataframe(df)
    if rips_df is None or rips_df.empty:
        return {
            "error": (
                "No se encontraron registros con ESTADO_COMPLETITUD = 'COMPLETO' "
                "después del filtrado. Verifica que el archivo tenga registros "
                "en ese estado."
            ),
            "rips_df": None,
        }

    doc_col = COLUMN_NAMES_RIPS["documento"]
    doc_col = doc_col[0] if isinstance(doc_col, list) else doc_col

    before = len(rips_df)

    rips_df = filter_by_billers_document(
        rips_df, df_facturadores,
        source_column=doc_col,
    )

    after = len(rips_df)

    if after == 0 and before > 0:
        return {
            "error": (
                f"Todos los {before} registros fueron filtrados porque ningún "
                "USUARIO_QUE_COMPLETA_RIPS coincide con los DOCUMENTO del listado de "
                "facturadores. Carga el archivo de facturadores o verifica que los "
                "documentos coincidan."
            ),
            "rips_df": None,
        }

    return {
        "error": None,
        "rips_df": rips_df,
        "total_rows": int(after),
        "rows_before_billers_filter": before,
    }


class RipsService:

    def __init__(
        self,
        repository: ParquetRepository,
        productivity_service: ProductivityService,
    ):
        self.repository = repository
        self.productivity_service = productivity_service

    def get_processed_data(self) -> pd.DataFrame:
        df = self.repository.load()
        if df is None:
            raise ValidationException("RIPS parquet file not found.")
        return df

    def get_metrics(
        self,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ):
        df = self.get_processed_data()

        filtered_df = filter_rips(
            df=df,
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
        )
        return self.productivity_service.calculate_record_productivity(
            filtered_df,
            user_column_variants=["NOMBRE_USUARIO"],
            date_column_variants=["FECHA_COMPLETADO_RIPS"],
            category="RIPS",
            seconds_per_record=SECONDS_PER_RECORD_RIPS,
        )
