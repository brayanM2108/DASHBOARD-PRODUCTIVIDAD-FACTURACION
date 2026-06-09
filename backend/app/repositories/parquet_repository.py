from pathlib import Path

import pandas as pd


class ParquetRepository:

    def __init__(self, parquet_file: str):
        self.parquet_file = Path(parquet_file)

    def load(self) -> pd.DataFrame | None:

        if not self.parquet_file.exists():
            return None

        return pd.read_parquet(self.parquet_file)

    def save(self, df: pd.DataFrame) -> bool:

        df.to_parquet(
            self.parquet_file,
            index=False,
        )

        return True

    def exists(self) -> bool:

        return self.parquet_file.exists()