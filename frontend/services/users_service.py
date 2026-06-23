from frontend.api.users_api import UsersApi


class UsersFrontendService:

    def __init__(self, token: str | None = None):
        self.api = UsersApi(token=token)

    def list_users(self, page: int = 1, size: int = 50, search: str | None = None, role_filter: str | None = None) -> dict:
        return self.api.list_users(page, size, search, role_filter)

    def get_user(self, user_id: int) -> dict:
        return self.api.get_user(user_id)

    def update_user(self, user_id: int, data: dict) -> dict:
        return self.api.update_user(user_id, data)

    def toggle_active(self, user_id: int) -> dict:
        return self.api.toggle_active(user_id)
