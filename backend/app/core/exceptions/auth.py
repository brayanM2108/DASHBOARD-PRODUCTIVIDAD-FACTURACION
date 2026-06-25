from .base import AppException


class InvalidCredentialsException(AppException):

    def __init__(self):
        super().__init__(
            message="Credenciales inválidas",
            status_code=401,
            error_code="INVALID_CREDENTIALS"
        )

class UserNotActivate(AppException):

    def __init__(self):
        super().__init__(
            message="Usuario no activo",
            status_code=401,
            error_code="USER_NOT_ACTIVATE"
        )

class UserAlreadyExist(AppException):

    def __init__(self):
        super().__init__(
            message="El usuario ya existe",
            status_code=409,
            error_code="USER_ALREADY_EXISTS"
        )
class EmailAlreadyExist(AppException):

    def __init__(self):
        super().__init__(
            message="El email ya existe",
            status_code=409,
            error_code="EMAIL_ALREADY_EXISTS"
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


class UserNotFoundException(AppException):

    def __init__(self, usernames: str | list[str]):
        names = usernames if isinstance(usernames, str) else ", ".join(usernames)
        super().__init__(
            message=f"Usuario(s) no encontrado(s): {names}",
            status_code=404,
            error_code="USER_NOT_FOUND",
        )