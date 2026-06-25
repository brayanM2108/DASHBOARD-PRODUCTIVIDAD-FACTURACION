"""Custom API exceptions for the frontend service layer."""


class ApiException(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UnauthorizedException(ApiException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class UserNotActiveException(ApiException):
    """Raised when the user account is not active."""

    def __init__(self, message: str = "Usuario no activo"):
        super().__init__(message, status_code=401)


class NotFoundException(ApiException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class UserAlreadyExistsException(ApiException):
    """Raised when the username already exists."""

    def __init__(self, message: str = "El usuario ya existe"):
        super().__init__(message, status_code=409)


class EmailAlreadyExistsException(ApiException):
    """Raised when the email already exists."""

    def __init__(self, message: str = "El email ya existe"):
        super().__init__(message, status_code=409)
