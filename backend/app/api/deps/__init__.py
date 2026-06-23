from .auth_deps import oauth2_scheme, get_current_user, require_roles, get_current_biller_name
from .repository_deps import (
    get_user_repository,
    get_legalizations_repository,
    get_electronic_billing_repository,
    get_administrative_process_repository,
    get_rips_repository,
    get_radicacion_repository,
)
from .service_deps import (
    get_auth_service,
    get_productivity_service,
    get_legalizations_service,
    get_electronic_billing_service,
    get_manual_billing_service,
    get_rips_service,
    get_radicacion_service,
    get_home_service,
    get_users_service,
)

__all__ = [
    "oauth2_scheme",
    "get_current_user",
    "require_roles",
    "get_current_biller_name",
    "get_user_repository",
    "get_legalizations_repository",
    "get_electronic_billing_repository",
    "get_administrative_process_repository",
    "get_rips_repository",
    "get_radicacion_repository",
    "get_auth_service",
    "get_productivity_service",
    "get_legalizations_service",
    "get_electronic_billing_service",
    "get_manual_billing_service",
    "get_rips_service",
    "get_radicacion_service",
    "get_home_service",
    "get_users_service",
]
