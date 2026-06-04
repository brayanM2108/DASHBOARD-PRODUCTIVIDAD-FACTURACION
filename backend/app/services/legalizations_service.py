from datetime import date

from ..etl.filters.legalizations_filter import filter_legalizations
from ..etl.transformers.legalizations_transformer import split_legalizations
from ..etl.validators.legalizations_validator import (
    validate_legalizations_dataframe,
)

from ..services.productivity_service import ProductivityService
from ..repositories.parquet_repository import ParquetRepository
from ..core.exceptions.business import (
    ValidationException
)


class LegalizationsService:

    def __init__(
            self,
            repository: ParquetRepository,
            productivity_service: ProductivityService,
    ):
        self.repository = repository
        self.productivity_service = productivity_service

    def get_processed_data(self):

        df = self.repository.get_dataframe()

        is_valid, message = validate_legalizations_dataframe(df)


        if not is_valid:
            raise ValidationException("Legalizations data is invalid: ")


        ppl_df, agreements_df = split_legalizations(df)

        return ppl_df, agreements_df

    def get_metrics(
            self,
            start_date: date,
            end_date: date,
            selected_users: list[str] | None = None,
    ):

        ppl_df, agreements_df = self.get_processed_data()

        ppl_df = filter_legalizations(
            df=ppl_df,
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
        )

        agreements_df = filter_legalizations(
            df=agreements_df,
            start_date=start_date,
            end_date=end_date,
            selected_users=selected_users,
        )

        return {
            "ppl": self.productivity_service.calculate_legalizations_productivity(
                ppl_df,
                category="PPL",
            ),
            "agreements": self.productivity_service.calculate_legalizations_productivity(
                agreements_df,
                category="Convenios",
            ),
        }
