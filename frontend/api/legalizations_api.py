from frontend.api.api_client import ApiClient


class LegalizationsApi:

    def __init__(self):
        self.client = ApiClient()

    def get_metrics(
            self,
            start_date,
            end_date,
            selected_users=None,
    ):


        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        if selected_users:
            params["selected_users"] = selected_users

        result = self.client.get(
            "/api/legalizations/metrics",
            params=params,
        )

        return result
