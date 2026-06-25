from datetime import date

import pandas as pd

from ..core.exceptions.business import ValidationException
from ..core.exceptions.auth import UserNotFoundException
from ..etl.billers_processor import filter_by_billers_master
from ..etl.filters.legalizations_filter import filter_legalizations
from ..etl.transformers.legalizations_transformer import (
    AGREEMENT_TYPE,
    LEGALIZATION_TYPE_COLUMN,
    PPL_TYPE,
    prepare_legalizations_dataframe,
)
from ..etl.validators.legalizations_validator import validate_legalizations_dataframe
from ..repositories.parquet_repository import ParquetRepository
from ..utils.config.settings import COLUMN_NAMES_LEGALIZATIONS, SECONDS_PER_RECORD_LEGALIZATIONS
from .productivity_service import ProductivityService
from ..etl.filters.legalizations_filter import validate_users_exist


def process_legalizations(df: pd.DataFrame, df_facturadores=None) -> dict:
    """Validate and normalize a raw legalizations upload into a unified dataframe."""
    if df is None or df.empty:
        return {
            "error": "El archivo de legalizaciones no contiene registros.",
            "legalizations_df": None,
        }

    is_valid, message = validate_legalizations_dataframe(df)
    if not is_valid:
        return {
            "error": message,
            "legalizations_df": None,
        }

    legalizations_df = prepare_legalizations_dataframe(df)
    if legalizations_df is None or legalizations_df.empty:
        return {
            "error": "No se encontraron registros válidos de legalizaciones.",
            "legalizations_df": None,
        }

    legalizations_df = filter_by_billers_master(
        legalizations_df, df_facturadores,
        document_column=COLUMN_NAMES_LEGALIZATIONS["documento"],
    )

    return {
        "error": None,
        "legalizations_df": legalizations_df,
        "total_rows": int(len(legalizations_df)),
        "ppl_count": int(
            legalizations_df[LEGALIZATION_TYPE_COLUMN]
            .astype(str)
            .str.strip()
            .str.upper()
            .eq(PPL_TYPE)
            .sum()
        ),
        "agreements_count": int(
            legalizations_df[LEGALIZATION_TYPE_COLUMN]
            .astype(str)
            .str.strip()
            .str.upper()
            .eq(AGREEMENT_TYPE)
            .sum()
        ),
    }


class LegalizationsService:

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
            raise ValidationException("Legalizations parquet file not found.")

        is_valid, message = validate_legalizations_dataframe(
            df,
            require_legalization_type=True,
        )

        if not is_valid:
            raise ValidationException(message)

        from ..etl.loaders.billers_loader import load_billers_master
        billers_df = load_billers_master()
        df = filter_by_billers_master(
            df, billers_df,
            document_column=COLUMN_NAMES_LEGALIZATIONS["documento"],
        )

        return df

    def _calculate_metrics_for_type(
        self,
        legalizations_df: pd.DataFrame,
        legalization_type: str,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ) -> dict:
        if selected_users and len(selected_users) > 0 and "Todos" not in selected_users and "All" not in selected_users:
            missing = validate_users_exist(legalizations_df, selected_users)
            if missing:
                raise UserNotFoundException(missing)

        filtered_df = filter_legalizations(
            df=legalizations_df,
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
            legalization_type=legalization_type,
        )
        return self.productivity_service.calculate_legalizations_productivity(
            filtered_df,
            category="PPL" if legalization_type == PPL_TYPE else "Convenios",
            seconds_per_record=SECONDS_PER_RECORD_LEGALIZATIONS,
        )

    def get_metrics(
            self,
            start_date: date,
            end_date: date,
            selected_users: list[str] | None = None,
    ):
        legalizations_df = self.get_processed_data()

        return {
            "ppl": self._calculate_metrics_for_type(
                legalizations_df=legalizations_df,
                legalization_type=PPL_TYPE,
                start_date=start_date,
                end_date=end_date,
                selected_users=selected_users,
            ),
            "agreements": self._calculate_metrics_for_type(
                legalizations_df=legalizations_df,
                legalization_type=AGREEMENT_TYPE,
                start_date=start_date,
                end_date=end_date,
                selected_users=selected_users,
            ),
        }
