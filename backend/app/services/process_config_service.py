import json
import os
from typing import Any

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "utils", "config", "process_config.json")


class ProcessConfigService:

    @staticmethod
    def _resolve_path() -> str:
        return os.path.abspath(_CONFIG_PATH)

    @classmethod
    def read_config(cls) -> dict[str, Any]:
        path = cls._resolve_path()
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def write_config(cls, data: dict[str, Any]) -> None:
        path = cls._resolve_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        from ..utils.config.settings import reload_config
        reload_config()
