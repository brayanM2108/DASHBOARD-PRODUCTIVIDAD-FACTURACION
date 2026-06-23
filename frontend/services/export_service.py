from datetime import date

from frontend.api.export_api import ExportApi


_MODULE_FILENAMES = {
    "general": "informe_general",
    "billing": "informe_facturacion",
    "legalizations": "informe_legalizaciones",
    "rips": "informe_rips",
    "radicacion": "informe_radicacion",
    "processes": "informe_procesos",
}


class ExportFrontendService:

    def __init__(self, token: str | None = None):
        self.api = ExportApi(token=token)

    def export_module(
        self,
        module: str,
        start_date: date,
        end_date: date,
        selected_users: list[str] | None = None,
    ) -> tuple[bytes, str]:
        """
        Export a module report. Returns (file_bytes, filename).

        Args:
            module: One of 'general', 'billing', 'legalizations', 'rips', 'radicacion', 'processes'
            start_date: Start date for the report period
            end_date: End date for the report period
            selected_users: Optional list of usernames to filter by

        Returns:
            Tuple of (file_bytes, filename)
        """
        export_methods = {
            "general": self.api.get_general_export,
            "billing": self.api.get_billing_export,
            "legalizations": self.api.get_legalizations_export,
            "rips": self.api.get_rips_export,
            "radicacion": self.api.get_radicacion_export,
            "processes": self.api.get_processes_export,
        }

        method = export_methods.get(module)
        if method is None:
            raise ValueError(f"Unknown module: {module}")

        file_bytes = method(start_date, end_date, selected_users)
        filename = f"{_MODULE_FILENAMES[module]}_{start_date}_{end_date}.xlsx"
        return file_bytes, filename
