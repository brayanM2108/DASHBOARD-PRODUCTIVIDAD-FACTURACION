# app/repositories/parquet_repository.py

from pathlib import Path
import pandas as pd


class ParquetRepository:

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)

    def load(self, filename: str) -> pd.DataFrame | None:

        file_path = self.data_path / filename

        if not file_path.exists():
            return None

        return pd.read_parquet(file_path)

    def save(self, df: pd.DataFrame, filename: str) -> bool:

        file_path = self.data_path / filename

        df.to_parquet(
            file_path,
            index=False
        )

        return True

    def exists(self, filename: str) -> bool:

        return (self.data_path / filename).exists()