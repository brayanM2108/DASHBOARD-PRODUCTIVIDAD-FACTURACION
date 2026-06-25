from frontend.api.process_config_api import ProcessConfigApi


class ProcessConfigFrontendService:

    def __init__(self, token: str | None = None):
        self.api = ProcessConfigApi(token=token)

    def get_config(self) -> dict:
        return self.api.get_config()

    def update_config(self, processes: list[dict], module_times: dict | None = None) -> dict:
        return self.api.update_config(processes, module_times)
