from .base import AppException


class ValidationException(AppException):

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR"
        )


class DataNotFoundException(AppException):

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=404,
            error_code="DATA_NOT_FOUND"
        )