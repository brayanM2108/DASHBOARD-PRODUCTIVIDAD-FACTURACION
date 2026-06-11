from .base import AppException


class InvalidCredentialsException(AppException):

    def __init__(self):
        super().__init__(
            message="Credenciales inválidas",
            status_code=401,
            error_code="INVALID_CREDENTIALS"
        )

class UserAlreadyExist(AppException):

    def __init__(self):
        super().__init__(
            message="El usuario ya existe",
            status_code=409,
            error_code="INVALID_RECORD"
        )
class EmailAlreadyExist(AppException):

    def __init__(self):
        super().__init__(
            message="El email ya existe",
            status_code=409,
            error_code="INVALID_RECORD"
        )

class InvalidTokenException(AppException):

    def __init__(self):
        super().__init__(
            message="Token inválido",
            status_code=401,
            error_code="INVALID_TOKEN"
        )


class ForbiddenException(AppException):

    def __init__(self):
        super().__init__(
            message="No autorizado",
            status_code=403,
            error_code="FORBIDDEN"
        )