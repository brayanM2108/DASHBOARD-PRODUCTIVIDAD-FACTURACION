from .base import AppException


class ParquetFileNotFoundException(AppException):

    def __init__(self, path: str):
        super().__init__(
            message=f"No existe el parquet: {path}",
            status_code=404,
            error_code="PARQUET_NOT_FOUND"
        )


class InvalidParquetException(AppException):

    def __init__(self):
        super().__init__(
            message="Parquet inválido",
            status_code=500,
            error_code="INVALID_PARQUET"
        )